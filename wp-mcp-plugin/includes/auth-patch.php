<?php
/**
 * MCP Authentication Functions - Patched Version
 * 
 * This version changes template editing to require 'manage_options' instead of 'edit_themes'
 * since some admin users might not have theme editing capabilities.
 */

// Check permissions for API endpoints
function mcp_check_permissions($request) {
    // First check if user is logged in via Application Password
    if (is_user_logged_in()) {
        // Check for required capabilities
        $user = wp_get_current_user();
        
        // For template editing, require manage_options (administrator capability)
        // Changed from 'edit_themes' to allow more flexibility
        $route = $request->get_route();
        if (strpos($route, '/templates') !== false) {
            return current_user_can('manage_options');  // Changed from 'edit_themes'
        }
        
        // For WooCommerce operations, require manage_woocommerce
        if (strpos($route, '/woocommerce') !== false) {
            return current_user_can('manage_woocommerce');
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
// Just need to ensure it's enabled
add_filter('wp_is_application_passwords_available', '__return_true');

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
            'MCP API Access: %s %s by user %d',
            $request->get_method(),
            $route,
            get_current_user_id()
        ));
    }
    
    return $result;
}

// Add CORS headers if needed (for local development)
add_action('rest_api_init', function() {
    remove_filter('rest_pre_serve_request', 'rest_send_cors_headers');
    add_filter('rest_pre_serve_request', function($value) {
        header('Access-Control-Allow-Origin: *');
        header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
        header('Access-Control-Allow-Headers: Authorization, Content-Type');
        header('Access-Control-Allow-Credentials: true');
        return $value;
    });
}, 15);
