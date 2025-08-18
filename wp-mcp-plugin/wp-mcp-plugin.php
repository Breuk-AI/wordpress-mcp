<?php
/**
 * Plugin Name: WordPress MCP Integration
 * Plugin URI: https://github.com/yourusername/wordpress-mcp
 * Description: Provides Model Context Protocol (MCP) server integration for comprehensive WordPress and WooCommerce control
 * Version: 1.0.0
 * Requires at least: 5.6
 * Requires PHP: 7.4
 * Author: WordPress MCP Contributors
 * Author URI: https://github.com/yourusername/wordpress-mcp
 * License: MIT
 * License URI: https://opensource.org/licenses/MIT
 * Text Domain: wp-mcp
 * Domain Path: /languages
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('WP_MCP_VERSION', '1.0.0');
define('WP_MCP_PLUGIN_PATH', plugin_dir_path(__FILE__));
define('WP_MCP_PLUGIN_URL', plugin_dir_url(__FILE__));
define('WP_MCP_API_NAMESPACE', 'mcp/v1');
define('WP_MCP_MIN_WP_VERSION', '5.6');
define('WP_MCP_MIN_PHP_VERSION', '7.4');

// Check minimum requirements
if (version_compare(PHP_VERSION, WP_MCP_MIN_PHP_VERSION, '<')) {
    add_action('admin_notices', function() {
        ?>
        <div class="notice notice-error">
            <p><?php printf(__('WordPress MCP Integration requires PHP %s or higher. You are running PHP %s.', 'wp-mcp'), WP_MCP_MIN_PHP_VERSION, PHP_VERSION); ?></p>
        </div>
        <?php
    });
    return;
}

// Include required files
require_once WP_MCP_PLUGIN_PATH . 'includes/api-endpoints.php';
require_once WP_MCP_PLUGIN_PATH . 'includes/auth.php';
require_once WP_MCP_PLUGIN_PATH . 'includes/backup-manager.php';

// Initialize the plugin
add_action('init', 'wp_mcp_init');
function wp_mcp_init() {
    // Load plugin textdomain for translations
    load_plugin_textdomain('wp-mcp', false, dirname(plugin_basename(__FILE__)) . '/languages');
    
    // Check WordPress version
    global $wp_version;
    if (version_compare($wp_version, WP_MCP_MIN_WP_VERSION, '<')) {
        add_action('admin_notices', function() {
            ?>
            <div class="notice notice-error">
                <p><?php printf(__('WordPress MCP Integration requires WordPress %s or higher.', 'wp-mcp'), WP_MCP_MIN_WP_VERSION); ?></p>
            </div>
            <?php
        });
        return;
    }
}

// Register REST API endpoints
add_action('rest_api_init', 'mcp_register_api_endpoints');

// Add admin menu
add_action('admin_menu', 'wp_mcp_add_admin_menu');
function wp_mcp_add_admin_menu() {
    add_menu_page(
        __('MCP Integration', 'wp-mcp'),
        __('MCP Integration', 'wp-mcp'),
        'manage_options',
        'wp-mcp-integration',
        'wp_mcp_admin_page',
        'dashicons-rest-api',
        90
    );
    
    // Add settings submenu
    add_submenu_page(
        'wp-mcp-integration',
        __('MCP Settings', 'wp-mcp'),
        __('Settings', 'wp-mcp'),
        'manage_options',
        'wp-mcp-settings',
        'wp_mcp_settings_page'
    );
}

// Admin page
function wp_mcp_admin_page() {
    ?>
    <div class="wrap">
        <h1><?php _e('WordPress MCP Integration', 'wp-mcp'); ?></h1>
        
        <div class="card">
            <h2><?php _e('Connection Status', 'wp-mcp'); ?></h2>
            <p><?php _e('MCP Server can connect to your WordPress site using Application Passwords.', 'wp-mcp'); ?></p>
            
            <h3><?php _e('Setup Instructions:', 'wp-mcp'); ?></h3>
            <ol>
                <li><?php _e('Go to Users → Your Profile', 'wp-mcp'); ?></li>
                <li><?php _e('Scroll down to "Application Passwords"', 'wp-mcp'); ?></li>
                <li><?php _e('Enter "MCP Server" as the name', 'wp-mcp'); ?></li>
                <li><?php _e('Click "Add New Application Password"', 'wp-mcp'); ?></li>
                <li><?php _e('Copy the generated password', 'wp-mcp'); ?></li>
                <li><?php _e('Add it to your MCP server .env file', 'wp-mcp'); ?></li>
            </ol>
        </div>
        
        <div class="card">
            <h2><?php _e('Available Endpoints', 'wp-mcp'); ?></h2>
            <p><?php _e('The following custom endpoints are available:', 'wp-mcp'); ?></p>
            <ul>
                <li><code>/wp-json/mcp/v1/templates</code> - <?php _e('List theme templates', 'wp-mcp'); ?></li>
                <li><code>/wp-json/mcp/v1/templates/read</code> - <?php _e('Read template content', 'wp-mcp'); ?></li>
                <li><code>/wp-json/mcp/v1/templates/update</code> - <?php _e('Update template content', 'wp-mcp'); ?></li>
                <li><code>/wp-json/mcp/v1/system/info</code> - <?php _e('Get system information', 'wp-mcp'); ?></li>
                <?php if (class_exists('WooCommerce')) : ?>
                <li><code>/wp-json/mcp/v1/woocommerce/bulk-update</code> - <?php _e('WooCommerce bulk operations', 'wp-mcp'); ?></li>
                <?php endif; ?>
            </ul>
        </div>
        
        <div class="card">
            <h2><?php _e('System Status', 'wp-mcp'); ?></h2>
            <?php wp_mcp_display_system_status(); ?>
        </div>
    </div>
    <?php
}

// Settings page
function wp_mcp_settings_page() {
    ?>
    <div class="wrap">
        <h1><?php _e('MCP Settings', 'wp-mcp'); ?></h1>
        
        <form method="post" action="options.php">
            <?php
            settings_fields('wp_mcp_settings');
            do_settings_sections('wp_mcp_settings');
            ?>
            
            <table class="form-table">
                <tr>
                    <th scope="row">
                        <label for="mcp_rate_limit"><?php _e('Rate Limit', 'wp-mcp'); ?></label>
                    </th>
                    <td>
                        <input type="number" id="mcp_rate_limit" name="mcp_rate_limit" 
                               value="<?php echo get_option('mcp_rate_limit', 60); ?>" />
                        <p class="description"><?php _e('Maximum API requests per minute per user', 'wp-mcp'); ?></p>
                    </td>
                </tr>
                
                <tr>
                    <th scope="row">
                        <label for="mcp_backup_retention"><?php _e('Backup Retention', 'wp-mcp'); ?></label>
                    </th>
                    <td>
                        <input type="number" id="mcp_backup_retention" name="mcp_backup_retention" 
                               value="<?php echo get_option('mcp_backup_retention', 7); ?>" />
                        <p class="description"><?php _e('Days to keep template backups', 'wp-mcp'); ?></p>
                    </td>
                </tr>
                
                <tr>
                    <th scope="row">
                        <label for="mcp_cors_origins"><?php _e('CORS Origins', 'wp-mcp'); ?></label>
                    </th>
                    <td>
                        <textarea id="mcp_cors_origins" name="mcp_cors_origins" rows="3" cols="50"><?php 
                            echo implode("\n", get_option('mcp_cors_origins', array())); 
                        ?></textarea>
                        <p class="description"><?php _e('Allowed origins for CORS (one per line). Leave empty for same-origin only.', 'wp-mcp'); ?></p>
                    </td>
                </tr>
                
                <tr>
                    <th scope="row">
                        <label for="mcp_debug_mode"><?php _e('Debug Mode', 'wp-mcp'); ?></label>
                    </th>
                    <td>
                        <input type="checkbox" id="mcp_debug_mode" name="mcp_debug_mode" value="1" 
                               <?php checked(get_option('mcp_debug_mode'), 1); ?> />
                        <label for="mcp_debug_mode"><?php _e('Enable debug logging', 'wp-mcp'); ?></label>
                    </td>
                </tr>
            </table>
            
            <?php submit_button(); ?>
        </form>
    </div>
    <?php
}

// Display system status
function wp_mcp_display_system_status() {
    global $wp_version;
    ?>
    <table class="widefat">
        <tbody>
            <tr>
                <td><?php _e('WordPress Version', 'wp-mcp'); ?></td>
                <td><?php echo $wp_version; ?></td>
            </tr>
            <tr>
                <td><?php _e('PHP Version', 'wp-mcp'); ?></td>
                <td><?php echo PHP_VERSION; ?></td>
            </tr>
            <tr>
                <td><?php _e('Application Passwords', 'wp-mcp'); ?></td>
                <td><?php echo wp_is_application_passwords_available() ? __('Enabled', 'wp-mcp') : __('Disabled', 'wp-mcp'); ?></td>
            </tr>
            <tr>
                <td><?php _e('WooCommerce', 'wp-mcp'); ?></td>
                <td><?php echo class_exists('WooCommerce') ? __('Active', 'wp-mcp') . ' (v' . WC()->version . ')' : __('Not Active', 'wp-mcp'); ?></td>
            </tr>
            <tr>
                <td><?php _e('Multisite', 'wp-mcp'); ?></td>
                <td><?php echo is_multisite() ? __('Yes', 'wp-mcp') : __('No', 'wp-mcp'); ?></td>
            </tr>
        </tbody>
    </table>
    <?php
}

// Register settings
add_action('admin_init', function() {
    register_setting('wp_mcp_settings', 'mcp_rate_limit', 'intval');
    register_setting('wp_mcp_settings', 'mcp_backup_retention', 'intval');
    register_setting('wp_mcp_settings', 'mcp_cors_origins', function($input) {
        $origins = explode("\n", $input);
        $sanitized = array();
        foreach ($origins as $origin) {
            $origin = trim($origin);
            if (!empty($origin)) {
                $sanitized[] = esc_url_raw($origin);
            }
        }
        return $sanitized;
    });
    register_setting('wp_mcp_settings', 'mcp_debug_mode', 'intval');
    
    // Define debug constant if enabled
    if (get_option('mcp_debug_mode')) {
        if (!defined('MCP_DEBUG')) {
            define('MCP_DEBUG', true);
        }
    }
});

// Activation hook
register_activation_hook(__FILE__, 'wp_mcp_activate');
function wp_mcp_activate() {
    // Set default options
    add_option('wp_mcp_version', WP_MCP_VERSION);
    add_option('mcp_rate_limit', 60);
    add_option('mcp_backup_retention', 7);
    add_option('mcp_cors_origins', array());
    add_option('mcp_debug_mode', 0);
    
    // Create backup directory
    $backup_dir = WP_CONTENT_DIR . '/mcp-backups';
    if (!file_exists($backup_dir)) {
        wp_mkdir_p($backup_dir);
        
        // Add .htaccess to protect backups
        file_put_contents($backup_dir . '/.htaccess', 'Deny from all');
    }
    
    // Schedule backup cleanup
    if (!wp_next_scheduled('wp_mcp_cleanup_backups')) {
        wp_schedule_event(time(), 'daily', 'wp_mcp_cleanup_backups');
    }
    
    // Flush rewrite rules to ensure our endpoints work
    flush_rewrite_rules();
}

// Deactivation hook
register_deactivation_hook(__FILE__, 'wp_mcp_deactivate');
function wp_mcp_deactivate() {
    // Clear scheduled events
    wp_clear_scheduled_hook('wp_mcp_cleanup_backups');
    
    // Flush rewrite rules
    flush_rewrite_rules();
}

// Uninstall hook (in separate uninstall.php file for proper cleanup)
