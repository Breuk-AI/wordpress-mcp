<?php
/**
 * MCP Capability Checker
 * 
 * Add this temporarily to your WordPress site to check what capabilities
 * the Application Password user has.
 * 
 * Usage: Create a page/post with this shortcode: [mcp_check_caps]
 */

// Shortcode to display current user capabilities
add_shortcode('mcp_check_caps', function() {
    if (!is_user_logged_in()) {
        return 'Not logged in';
    }
    
    $user = wp_get_current_user();
    $caps = $user->allcaps;
    
    $output = '<h3>Current User: ' . $user->user_login . '</h3>';
    $output .= '<h4>User Roles:</h4><ul>';
    foreach ($user->roles as $role) {
        $output .= '<li>' . $role . '</li>';
    }
    $output .= '</ul>';
    
    $output .= '<h4>Key Capabilities:</h4><ul>';
    $important_caps = ['manage_options', 'edit_themes', 'manage_woocommerce', 'edit_posts', 'edit_pages'];
    foreach ($important_caps as $cap) {
        $has_cap = isset($caps[$cap]) && $caps[$cap] ? '✅' : '❌';
        $output .= '<li>' . $cap . ': ' . $has_cap . '</li>';
    }
    $output .= '</ul>';
    
    return $output;
});
