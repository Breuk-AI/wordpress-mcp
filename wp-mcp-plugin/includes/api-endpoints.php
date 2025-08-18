<?php
/**
 * MCP Custom API Endpoints
 */

// Register all custom endpoints
function mcp_register_api_endpoints() {
    // Template management endpoints
    register_rest_route(MCP_API_NAMESPACE, '/templates', array(
        'methods' => 'GET',
        'callback' => 'mcp_get_templates',
        'permission_callback' => 'mcp_check_permissions',
    ));
    
    register_rest_route(MCP_API_NAMESPACE, '/templates/read', array(
        'methods' => 'POST',
        'callback' => 'mcp_read_template',
        'permission_callback' => 'mcp_check_permissions',
    ));
    
    register_rest_route(MCP_API_NAMESPACE, '/templates/update', array(
        'methods' => 'POST',
        'callback' => 'mcp_update_template',
        'permission_callback' => 'mcp_check_permissions',
    ));
    
    // System information
    register_rest_route(MCP_API_NAMESPACE, '/system/info', array(
        'methods' => 'GET',
        'callback' => 'mcp_get_system_info',
        'permission_callback' => 'mcp_check_permissions',
    ));
    
    // WooCommerce extensions (if needed beyond standard API)
    register_rest_route(MCP_API_NAMESPACE, '/woocommerce/bulk-update', array(
        'methods' => 'POST',
        'callback' => 'mcp_wc_bulk_update',
        'permission_callback' => 'mcp_check_permissions',
    ));
}

// Get list of theme templates
function mcp_get_templates($request) {
    $theme = wp_get_theme();
    $templates = array();
    
    // Get theme directory
    $theme_dir = get_template_directory();
    $child_theme_dir = get_stylesheet_directory();
    
    // Scan for PHP template files
    $files = array();
    
    // Parent theme files
    $parent_files = glob($theme_dir . '/*.php');
    foreach ($parent_files as $file) {
        $files[] = array(
            'path' => str_replace($theme_dir . '/', '', $file),
            'theme' => $theme->get('Name'),
            'type' => 'parent',
            'full_path' => $file
        );
    }
    
    // Child theme files (if active)
    if ($child_theme_dir !== $theme_dir) {
        $child_files = glob($child_theme_dir . '/*.php');
        foreach ($child_files as $file) {
            $files[] = array(
                'path' => str_replace($child_theme_dir . '/', '', $file),
                'theme' => wp_get_theme()->get('Name'),
                'type' => 'child',
                'full_path' => $file
            );
        }
    }
    
    // Also get template parts
    $template_parts = array('template-parts', 'parts', 'partials');
    foreach ($template_parts as $dir) {
        if (is_dir($theme_dir . '/' . $dir)) {
            $part_files = glob($theme_dir . '/' . $dir . '/*.php');
            foreach ($part_files as $file) {
                $files[] = array(
                    'path' => str_replace($theme_dir . '/', '', $file),
                    'theme' => $theme->get('Name'),
                    'type' => 'part',
                    'full_path' => $file
                );
            }
        }
    }
    
    return rest_ensure_response($files);
}

// Read template content
function mcp_read_template($request) {
    $params = $request->get_json_params();
    $template_path = $params['path'] ?? '';
    
    if (empty($template_path)) {
        return new WP_Error('missing_path', 'Template path is required', array('status' => 400));
    }
    
    // Security: Ensure path doesn't go outside theme directory
    $theme_dir = get_template_directory();
    $child_theme_dir = get_stylesheet_directory();
    
    // Try child theme first, then parent
    $full_path = '';
    if (file_exists($child_theme_dir . '/' . $template_path)) {
        $full_path = $child_theme_dir . '/' . $template_path;
    } elseif (file_exists($theme_dir . '/' . $template_path)) {
        $full_path = $theme_dir . '/' . $template_path;
    }
    
    if (empty($full_path) || !file_exists($full_path)) {
        return new WP_Error('not_found', 'Template not found', array('status' => 404));
    }
    
    // Read file content
    $content = file_get_contents($full_path);
    
    return rest_ensure_response(array(
        'path' => $template_path,
        'content' => $content,
        'writable' => is_writable($full_path)
    ));
}

// Update template content
function mcp_update_template($request) {
    $params = $request->get_json_params();
    $template_path = $params['path'] ?? '';
    $content = $params['content'] ?? '';
    
    if (empty($template_path) || !isset($params['content'])) {
        return new WP_Error('missing_params', 'Path and content are required', array('status' => 400));
    }
    
    // Security checks
    $theme_dir = get_template_directory();
    $child_theme_dir = get_stylesheet_directory();
    
    // Determine full path
    $full_path = '';
    if (file_exists($child_theme_dir . '/' . $template_path)) {
        $full_path = $child_theme_dir . '/' . $template_path;
    } elseif (file_exists($theme_dir . '/' . $template_path)) {
        $full_path = $theme_dir . '/' . $template_path;
    }
    
    if (empty($full_path) || !file_exists($full_path)) {
        return new WP_Error('not_found', 'Template not found', array('status' => 404));
    }
    
    if (!is_writable($full_path)) {
        return new WP_Error('not_writable', 'Template is not writable', array('status' => 403));
    }
    
    // Backup original file
    $backup_path = $full_path . '.mcp-backup-' . date('Y-m-d-H-i-s');
    copy($full_path, $backup_path);
    
    // Write new content
    $result = file_put_contents($full_path, $content);
    
    if ($result === false) {
        return new WP_Error('write_failed', 'Failed to write template', array('status' => 500));
    }
    
    return rest_ensure_response(array(
        'success' => true,
        'message' => 'Template updated successfully',
        'backup_path' => $backup_path
    ));
}

// Get system information
function mcp_get_system_info($request) {
    global $wp_version;
    
    $info = array(
        'wordpress' => array(
            'version' => $wp_version,
            'site_url' => get_site_url(),
            'home_url' => get_home_url(),
            'is_multisite' => is_multisite(),
            'active_theme' => wp_get_theme()->get('Name'),
            'active_plugins' => get_option('active_plugins', array()),
        ),
        'php' => array(
            'version' => PHP_VERSION,
            'memory_limit' => ini_get('memory_limit'),
            'max_execution_time' => ini_get('max_execution_time'),
            'upload_max_filesize' => ini_get('upload_max_filesize'),
        ),
        'server' => array(
            'software' => $_SERVER['SERVER_SOFTWARE'] ?? 'Unknown',
        )
    );
    
    // Add WooCommerce info if active
    if (class_exists('WooCommerce')) {
        $info['woocommerce'] = array(
            'version' => WC()->version,
            'currency' => get_woocommerce_currency(),
            'base_location' => wc_get_base_location(),
        );
    }
    
    return rest_ensure_response($info);
}

// WooCommerce bulk operations
function mcp_wc_bulk_update($request) {
    if (!class_exists('WooCommerce')) {
        return new WP_Error('wc_not_active', 'WooCommerce is not active', array('status' => 400));
    }
    
    $params = $request->get_json_params();
    $operation = $params['operation'] ?? '';
    $items = $params['items'] ?? array();
    
    $results = array();
    
    switch ($operation) {
        case 'update_prices':
            foreach ($items as $item) {
                $product = wc_get_product($item['id']);
                if ($product) {
                    if (isset($item['regular_price'])) {
                        $product->set_regular_price($item['regular_price']);
                    }
                    if (isset($item['sale_price'])) {
                        $product->set_sale_price($item['sale_price']);
                    }
                    $product->save();
                    $results[] = array('id' => $item['id'], 'success' => true);
                } else {
                    $results[] = array('id' => $item['id'], 'success' => false, 'error' => 'Product not found');
                }
            }
            break;
            
        case 'update_stock':
            foreach ($items as $item) {
                $product = wc_get_product($item['id']);
                if ($product) {
                    $product->set_stock_quantity($item['stock_quantity']);
                    $product->set_stock_status($item['stock_quantity'] > 0 ? 'instock' : 'outofstock');
                    $product->save();
                    $results[] = array('id' => $item['id'], 'success' => true);
                } else {
                    $results[] = array('id' => $item['id'], 'success' => false, 'error' => 'Product not found');
                }
            }
            break;
            
        default:
            return new WP_Error('invalid_operation', 'Invalid bulk operation', array('status' => 400));
    }
    
    return rest_ensure_response(array(
        'operation' => $operation,
        'processed' => count($results),
        'results' => $results
    ));
}
