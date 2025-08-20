<?php
/**
 * MCP Custom API Endpoints - SECURITY PATCHED VERSION
 */

// Register all custom endpoints
function mcp_register_api_endpoints() {
    // Template management endpoints
    register_rest_route(WP_MCP_API_NAMESPACE, '/templates', array(
        'methods' => 'GET',
        'callback' => 'mcp_get_templates',
        'permission_callback' => 'mcp_check_permissions',
    ));
    
    register_rest_route(WP_MCP_API_NAMESPACE, '/templates/read', array(
        'methods' => 'POST',
        'callback' => 'mcp_read_template',
        'permission_callback' => 'mcp_check_permissions',
    ));
    
    register_rest_route(WP_MCP_API_NAMESPACE, '/templates/update', array(
        'methods' => 'POST',
        'callback' => 'mcp_update_template',
        'permission_callback' => 'mcp_check_permissions',
    ));
    
    // System information
    register_rest_route(WP_MCP_API_NAMESPACE, '/system/info', array(
        'methods' => 'GET',
        'callback' => 'mcp_get_system_info',
        'permission_callback' => 'mcp_check_permissions',
    ));
    
    // WooCommerce extensions (if needed beyond standard API)
    register_rest_route(WP_MCP_API_NAMESPACE, '/woocommerce/bulk-update', array(
        'methods' => 'POST',
        'callback' => 'mcp_wc_bulk_update',
        'permission_callback' => 'mcp_check_permissions',
    ));
}

// SECURITY: Validate template path to prevent directory traversal
function mcp_validate_template_path($path) {
    // Remove any directory traversal attempts
    $path = str_replace('..', '', $path);
    $path = str_replace('//', '/', $path);
    $path = ltrim($path, '/');
    
    // Only allow PHP files
    if (!preg_match('/\.php$/i', $path)) {
        return false;
    }
    
    // Check if path is within theme directories
    $theme_dir = get_template_directory();
    $child_theme_dir = get_stylesheet_directory();
    
    $full_path_parent = realpath($theme_dir . '/' . $path);
    $full_path_child = realpath($child_theme_dir . '/' . $path);
    
    // Ensure the resolved path is actually within theme directories
    if ($full_path_parent && strpos($full_path_parent, realpath($theme_dir)) === 0) {
        return $full_path_parent;
    }
    
    if ($full_path_child && strpos($full_path_child, realpath($child_theme_dir)) === 0) {
        return $full_path_child;
    }
    
    return false;
}

// Get list of theme templates
function mcp_get_templates($request) {
    $theme = wp_get_theme();
    $templates = array();
    
    // Get theme directory
    $theme_dir = get_template_directory();
    $child_theme_dir = get_stylesheet_directory();
    
    // Define allowed directories to scan
    $allowed_dirs = array('', 'template-parts', 'parts', 'partials', 'templates');
    
    $files = array();
    
    foreach ($allowed_dirs as $dir) {
        $scan_dir = $theme_dir;
        if (!empty($dir)) {
            $scan_dir .= '/' . $dir;
        }
        
        if (is_dir($scan_dir)) {
            // Only get PHP files, no subdirectory traversal
            $php_files = glob($scan_dir . '/*.php');
            foreach ($php_files as $file) {
                // Verify file is within theme directory
                if (strpos(realpath($file), realpath($theme_dir)) === 0) {
                    $files[] = array(
                        'path' => str_replace($theme_dir . '/', '', $file),
                        'theme' => $theme->get('Name'),
                        'type' => empty($dir) ? 'root' : 'part',
                        'readable' => is_readable($file),
                        'writable' => is_writable($file)
                    );
                }
            }
        }
    }
    
    // Also check child theme if active
    if ($child_theme_dir !== $theme_dir) {
        foreach ($allowed_dirs as $dir) {
            $scan_dir = $child_theme_dir;
            if (!empty($dir)) {
                $scan_dir .= '/' . $dir;
            }
            
            if (is_dir($scan_dir)) {
                $php_files = glob($scan_dir . '/*.php');
                foreach ($php_files as $file) {
                    if (strpos(realpath($file), realpath($child_theme_dir)) === 0) {
                        $files[] = array(
                            'path' => str_replace($child_theme_dir . '/', '', $file),
                            'theme' => wp_get_theme()->get('Name'),
                            'type' => 'child',
                            'readable' => is_readable($file),
                            'writable' => is_writable($file)
                        );
                    }
                }
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
    
    // SECURITY: Validate and sanitize path
    $full_path = mcp_validate_template_path($template_path);
    
    if (!$full_path) {
        return new WP_Error('invalid_path', 'Invalid template path or file type', array('status' => 400));
    }
    
    if (!file_exists($full_path)) {
        return new WP_Error('not_found', 'Template not found', array('status' => 404));
    }
    
    if (!is_readable($full_path)) {
        return new WP_Error('not_readable', 'Template is not readable', array('status' => 403));
    }
    
    // Read file content
    $content = file_get_contents($full_path);
    
    return rest_ensure_response(array(
        'path' => basename($full_path),
        'content' => $content,
        'writable' => is_writable($full_path),
        'size' => filesize($full_path),
        'modified' => filemtime($full_path)
    ));
}

// Update template content
function mcp_update_template($request) {
    // SECURITY: Require HTTPS for template updates
    if (!is_ssl() && !defined('WP_DEBUG')) {
        return new WP_Error('https_required', 'HTTPS connection required for template updates', array('status' => 403));
    }
    
    $params = $request->get_json_params();
    $template_path = $params['path'] ?? '';
    $content = $params['content'] ?? '';
    
    if (empty($template_path) || !isset($params['content'])) {
        return new WP_Error('missing_params', 'Path and content are required', array('status' => 400));
    }
    
    // SECURITY: Validate and sanitize path
    $full_path = mcp_validate_template_path($template_path);
    
    if (!$full_path) {
        return new WP_Error('invalid_path', 'Invalid template path or file type', array('status' => 400));
    }
    
    if (!file_exists($full_path)) {
        return new WP_Error('not_found', 'Template not found', array('status' => 404));
    }
    
    if (!is_writable($full_path)) {
        return new WP_Error('not_writable', 'Template is not writable', array('status' => 403));
    }
    
    // SECURITY: Basic PHP syntax validation
    if (strpos($content, '<?php') !== false) {
        // Check for obvious dangerous functions
        $dangerous_functions = array('eval', 'exec', 'system', 'shell_exec', 'passthru', 'assert');
        foreach ($dangerous_functions as $func) {
            if (preg_match('/\b' . preg_quote($func) . '\s*\(/i', $content)) {
                return new WP_Error('dangerous_code', 'Template contains potentially dangerous code', array('status' => 400));
            }
        }
    }
    
    // Create backup with timestamp
    $backup_dir = WP_CONTENT_DIR . '/mcp-backups/' . date('Y-m-d');
    if (!file_exists($backup_dir)) {
        wp_mkdir_p($backup_dir);
        // Protect backup directory
        file_put_contents($backup_dir . '/.htaccess', 'Deny from all');
    }
    
    $backup_path = $backup_dir . '/' . basename($full_path) . '-' . time() . '.bak';
    if (!copy($full_path, $backup_path)) {
        return new WP_Error('backup_failed', 'Failed to create backup', array('status' => 500));
    }
    
    // Write new content
    $result = file_put_contents($full_path, $content, LOCK_EX);
    
    if ($result === false) {
        // Restore from backup
        copy($backup_path, $full_path);
        return new WP_Error('write_failed', 'Failed to write template', array('status' => 500));
    }
    
    // Clear any caches
    if (function_exists('wp_cache_flush')) {
        wp_cache_flush();
    }
    
    return rest_ensure_response(array(
        'success' => true,
        'message' => 'Template updated successfully',
        'backup_created' => basename($backup_path),
        'bytes_written' => $result
    ));
}

// Get system information
function mcp_get_system_info($request) {
    global $wp_version;
    
    // SECURITY: Only return non-sensitive information
    $info = array(
        'wordpress' => array(
            'version' => $wp_version,
            'site_url' => get_site_url(),
            'is_multisite' => is_multisite(),
            'active_theme' => wp_get_theme()->get('Name'),
            'plugin_count' => count(get_option('active_plugins', array())),
        ),
        'php' => array(
            'version' => phpversion(),
            'memory_limit' => ini_get('memory_limit'),
        ),
        'mcp' => array(
            'version' => WP_MCP_VERSION,
            'rate_limit' => get_option('mcp_rate_limit', 60),
            'https_enabled' => is_ssl()
        )
    );
    
    // Add WooCommerce info if active
    if (class_exists('WooCommerce')) {
        $info['woocommerce'] = array(
            'version' => WC()->version,
            'currency' => get_woocommerce_currency(),
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
    $operation = sanitize_text_field($params['operation'] ?? '');
    $items = $params['items'] ?? array();
    
    // Limit bulk operations to prevent abuse
    if (count($items) > 100) {
        return new WP_Error('too_many_items', 'Maximum 100 items per bulk operation', array('status' => 400));
    }
    
    $results = array();
    
    switch ($operation) {
        case 'update_prices':
            foreach ($items as $item) {
                $product_id = intval($item['id'] ?? 0);
                if (!$product_id) continue;
                
                $product = wc_get_product($product_id);
                if ($product) {
                    if (isset($item['regular_price'])) {
                        $product->set_regular_price(floatval($item['regular_price']));
                    }
                    if (isset($item['sale_price'])) {
                        $product->set_sale_price(floatval($item['sale_price']));
                    }
                    $product->save();
                    $results[] = array('id' => $product_id, 'success' => true);
                } else {
                    $results[] = array('id' => $product_id, 'success' => false, 'error' => 'Product not found');
                }
            }
            break;
            
        case 'update_stock':
            foreach ($items as $item) {
                $product_id = intval($item['id'] ?? 0);
                if (!$product_id) continue;
                
                $product = wc_get_product($product_id);
                if ($product) {
                    $stock_qty = intval($item['stock_quantity'] ?? 0);
                    $product->set_stock_quantity($stock_qty);
                    $product->set_stock_status($stock_qty > 0 ? 'instock' : 'outofstock');
                    $product->save();
                    $results[] = array('id' => $product_id, 'success' => true);
                } else {
                    $results[] = array('id' => $product_id, 'success' => false, 'error' => 'Product not found');
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
