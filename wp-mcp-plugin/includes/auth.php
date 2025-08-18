<?php
/**
 * MCP Authentication Functions
 */

// Check permissions for API endpoints
function mcp_check_permissions($request) {
    // First check if user is logged in via Application Password
    if (is_user_logged_in()) {
        // Check for required capabilities
        $user = wp_get_current_user();
        
        // For template editing, require edit_themes capability
        $route = $request->get_route();
        if (strpos($route, '/templates') !== false) {
            return current_user_can('edit_themes') || current_user_can('manage_options');
        }
        
        // For WooCommerce operations, require manage_woocommerce
        if (strpos($route, '/woocommerce') !== false) {
            return current_user_can('manage_woocommerce') || current_user_can('manage_options');
        }
        
        // For general operations, require manage_options
        return current_user_can('manage_options');
    }
    
    // Not authenticated
    return new WP_Error(
        'rest_forbidden',
        'You must be authenticated to use this endpoint.',
        array('status' => 401)
    );
}

// Add support for Application Passwords (already built into WordPress 5.6+)
add_filter('wp_is_application_passwords_available', '__return_true');

// Rate limiting implementation
function mcp_check_rate_limit($user_id) {
    $rate_limit = get_option('mcp_rate_limit', 60);  // Default 60 requests per minute
    $transient_key = 'mcp_rate_limit_' . $user_id;
    $requests = get_transient($transient_key);
    
    if ($requests === false) {
        set_transient($transient_key, 1, 60);  // Reset every minute
        return true;
    }
    
    if ($requests >= $rate_limit) {
        return false;
    }
    
    set_transient($transient_key, $requests + 1, 60);
    return true;
}

// Add rate limiting to API requests
add_filter('rest_pre_dispatch', function($result, $server, $request) {
    $route = $request->get_route();
    
    // Only apply to MCP routes
    if (strpos($route, '/mcp/') !== false) {
        $user_id = get_current_user_id();
        
        if ($user_id && !mcp_check_rate_limit($user_id)) {
            return new WP_Error(
                'rate_limit_exceeded',
                'Too many requests. Please try again later.',
                array('status' => 429)
            );
        }
    }
    
    return $result;
}, 10, 3);

// Log API access for debugging (optional)
add_action('rest_api_init', function() {
    if (defined('MCP_DEBUG') && MCP_DEBUG) {
        add_filter('rest_pre_dispatch', 'mcp_log_api_access', 10, 3);
    }
});

function mcp_log_api_access($result, $server, $request) {
    $route = $request->get_route();
    
    // Only log MCP routes
    if (strpos($route, '/mcp/') !== false) {
        error_log(sprintf(
            'MCP API Access: %s %s by user %d at %s',
            $request->get_method(),
            $route,
            get_current_user_id(),
            current_time('mysql')
        ));
    }
    
    return $result;
}

// Add CORS headers with proper security
add_action('rest_api_init', function() {
    remove_filter('rest_pre_serve_request', 'rest_send_cors_headers');
    add_filter('rest_pre_serve_request', function($value) {
        // Get allowed origins from settings
        $allowed_origins = get_option('mcp_cors_origins', array());
        
        // If no origins configured, use same-origin policy (most secure)
        if (empty($allowed_origins)) {
            // Don't set CORS headers - browser will enforce same-origin
            return $value;
        }
        
        // Check if the request origin is allowed
        $origin = isset($_SERVER['HTTP_ORIGIN']) ? $_SERVER['HTTP_ORIGIN'] : '';
        
        if (in_array($origin, $allowed_origins, true)) {
            header('Access-Control-Allow-Origin: ' . $origin);
            header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
            header('Access-Control-Allow-Headers: Authorization, Content-Type, X-WP-Nonce');
            header('Access-Control-Allow-Credentials: true');
            header('Access-Control-Max-Age: 3600');
        }
        
        return $value;
    });
}, 15);

// Input sanitization helper
function mcp_sanitize_input($input, $type = 'text') {
    switch ($type) {
        case 'html':
            return wp_kses_post($input);
        case 'url':
            return esc_url_raw($input);
        case 'email':
            return sanitize_email($input);
        case 'filename':
            return sanitize_file_name($input);
        case 'number':
            return intval($input);
        case 'text':
        default:
            return sanitize_text_field($input);
    }
}

// Nonce verification for additional security
function mcp_verify_nonce($request) {
    $nonce = $request->get_header('X-WP-Nonce');
    
    if (!$nonce) {
        // Fall back to Application Password auth
        return true;
    }
    
    return wp_verify_nonce($nonce, 'wp_rest');
}
