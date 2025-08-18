<?php
/**
 * Backup Manager for WordPress MCP
 * Handles backup creation and cleanup for template edits
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Create a backup of a file
 * 
 * @param string $file_path Full path to the file to backup
 * @param string $type Type of backup (template, config, etc.)
 * @return string|false Path to backup file or false on failure
 */
function wp_mcp_create_backup($file_path, $type = 'template') {
    if (!file_exists($file_path)) {
        return false;
    }
    
    // Create backup directory if it doesn't exist
    $backup_dir = WP_CONTENT_DIR . '/mcp-backups';
    if (!file_exists($backup_dir)) {
        wp_mkdir_p($backup_dir);
        file_put_contents($backup_dir . '/.htaccess', 'Deny from all');
    }
    
    // Create subdirectory for this backup type
    $type_dir = $backup_dir . '/' . sanitize_file_name($type);
    if (!file_exists($type_dir)) {
        wp_mkdir_p($type_dir);
    }
    
    // Generate backup filename
    $file_info = pathinfo($file_path);
    $backup_filename = sprintf(
        '%s_%s_%s.backup',
        sanitize_file_name($file_info['filename']),
        date('Y-m-d_H-i-s'),
        wp_generate_password(8, false)
    );
    
    if (isset($file_info['extension'])) {
        $backup_filename .= '.' . $file_info['extension'];
    }
    
    $backup_path = $type_dir . '/' . $backup_filename;
    
    // Copy file to backup location
    if (copy($file_path, $backup_path)) {
        // Store backup metadata
        $backups = get_option('wp_mcp_backups', array());
        $backups[] = array(
            'original_path' => $file_path,
            'backup_path' => $backup_path,
            'type' => $type,
            'timestamp' => time(),
            'user_id' => get_current_user_id()
        );
        update_option('wp_mcp_backups', $backups);
        
        return $backup_path;
    }
    
    return false;
}

/**
 * Restore a file from backup
 * 
 * @param string $backup_path Path to the backup file
 * @param string $restore_path Path where to restore the file
 * @return bool Success or failure
 */
function wp_mcp_restore_backup($backup_path, $restore_path = null) {
    if (!file_exists($backup_path)) {
        return false;
    }
    
    // Get original path from metadata if not provided
    if ($restore_path === null) {
        $backups = get_option('wp_mcp_backups', array());
        foreach ($backups as $backup) {
            if ($backup['backup_path'] === $backup_path) {
                $restore_path = $backup['original_path'];
                break;
            }
        }
    }
    
    if (!$restore_path) {
        return false;
    }
    
    // Create a backup of current file before restoring
    if (file_exists($restore_path)) {
        wp_mcp_create_backup($restore_path, 'pre-restore');
    }
    
    // Restore the file
    return copy($backup_path, $restore_path);
}

/**
 * List available backups
 * 
 * @param array $filters Optional filters (type, date_from, date_to, etc.)
 * @return array List of backups
 */
function wp_mcp_list_backups($filters = array()) {
    $backups = get_option('wp_mcp_backups', array());
    
    // Apply filters
    if (!empty($filters['type'])) {
        $backups = array_filter($backups, function($backup) use ($filters) {
            return $backup['type'] === $filters['type'];
        });
    }
    
    if (!empty($filters['date_from'])) {
        $backups = array_filter($backups, function($backup) use ($filters) {
            return $backup['timestamp'] >= strtotime($filters['date_from']);
        });
    }
    
    if (!empty($filters['date_to'])) {
        $backups = array_filter($backups, function($backup) use ($filters) {
            return $backup['timestamp'] <= strtotime($filters['date_to']);
        });
    }
    
    // Sort by timestamp (newest first)
    usort($backups, function($a, $b) {
        return $b['timestamp'] - $a['timestamp'];
    });
    
    return $backups;
}

/**
 * Clean up old backups
 * 
 * @param int $retention_days Number of days to keep backups
 * @param string $type Optional type filter
 * @return int Number of backups deleted
 */
function wp_mcp_cleanup_old_backups($retention_days = null, $type = null) {
    if ($retention_days === null) {
        $retention_days = get_option('mcp_backup_retention', 7);
    }
    
    $cutoff_time = time() - ($retention_days * DAY_IN_SECONDS);
    $backups = get_option('wp_mcp_backups', array());
    $deleted_count = 0;
    $remaining_backups = array();
    
    foreach ($backups as $backup) {
        // Skip if type filter doesn't match
        if ($type !== null && $backup['type'] !== $type) {
            $remaining_backups[] = $backup;
            continue;
        }
        
        // Delete if older than retention period
        if ($backup['timestamp'] < $cutoff_time) {
            if (file_exists($backup['backup_path'])) {
                unlink($backup['backup_path']);
                $deleted_count++;
            }
        } else {
            $remaining_backups[] = $backup;
        }
    }
    
    // Update the backups list
    update_option('wp_mcp_backups', $remaining_backups);
    
    // Log cleanup activity
    if (defined('MCP_DEBUG') && MCP_DEBUG) {
        error_log(sprintf(
            'MCP Backup Cleanup: Deleted %d backups older than %d days',
            $deleted_count,
            $retention_days
        ));
    }
    
    return $deleted_count;
}

/**
 * Get backup statistics
 * 
 * @return array Statistics about backups
 */
function wp_mcp_get_backup_stats() {
    $backups = get_option('wp_mcp_backups', array());
    $backup_dir = WP_CONTENT_DIR . '/mcp-backups';
    
    $stats = array(
        'total_backups' => count($backups),
        'by_type' => array(),
        'total_size' => 0,
        'oldest_backup' => null,
        'newest_backup' => null
    );
    
    foreach ($backups as $backup) {
        // Count by type
        if (!isset($stats['by_type'][$backup['type']])) {
            $stats['by_type'][$backup['type']] = 0;
        }
        $stats['by_type'][$backup['type']]++;
        
        // Calculate size
        if (file_exists($backup['backup_path'])) {
            $stats['total_size'] += filesize($backup['backup_path']);
        }
        
        // Track oldest and newest
        if ($stats['oldest_backup'] === null || $backup['timestamp'] < $stats['oldest_backup']) {
            $stats['oldest_backup'] = $backup['timestamp'];
        }
        if ($stats['newest_backup'] === null || $backup['timestamp'] > $stats['newest_backup']) {
            $stats['newest_backup'] = $backup['timestamp'];
        }
    }
    
    // Format size
    $stats['total_size_formatted'] = size_format($stats['total_size']);
    
    return $stats;
}

// Schedule cleanup cron job
add_action('wp_mcp_cleanup_backups', 'wp_mcp_scheduled_backup_cleanup');
function wp_mcp_scheduled_backup_cleanup() {
    wp_mcp_cleanup_old_backups();
}

// Add admin interface for backup management
add_action('admin_menu', function() {
    add_submenu_page(
        'wp-mcp-integration',
        __('Backup Manager', 'wp-mcp'),
        __('Backups', 'wp-mcp'),
        'manage_options',
        'wp-mcp-backups',
        'wp_mcp_backups_page'
    );
});

// Backup management page
function wp_mcp_backups_page() {
    // Handle restore action
    if (isset($_POST['restore_backup']) && wp_verify_nonce($_POST['_wpnonce'], 'mcp_restore_backup')) {
        $backup_path = sanitize_text_field($_POST['backup_path']);
        if (wp_mcp_restore_backup($backup_path)) {
            echo '<div class="notice notice-success"><p>' . __('Backup restored successfully!', 'wp-mcp') . '</p></div>';
        } else {
            echo '<div class="notice notice-error"><p>' . __('Failed to restore backup.', 'wp-mcp') . '</p></div>';
        }
    }
    
    // Handle cleanup action
    if (isset($_POST['cleanup_backups']) && wp_verify_nonce($_POST['_wpnonce'], 'mcp_cleanup_backups')) {
        $deleted = wp_mcp_cleanup_old_backups();
        echo '<div class="notice notice-success"><p>' . sprintf(__('Cleaned up %d old backups.', 'wp-mcp'), $deleted) . '</p></div>';
    }
    
    $stats = wp_mcp_get_backup_stats();
    $backups = wp_mcp_list_backups();
    
    ?>
    <div class="wrap">
        <h1><?php _e('Backup Manager', 'wp-mcp'); ?></h1>
        
        <div class="card">
            <h2><?php _e('Backup Statistics', 'wp-mcp'); ?></h2>
            <p><?php printf(__('Total Backups: %d', 'wp-mcp'), $stats['total_backups']); ?></p>
            <p><?php printf(__('Total Size: %s', 'wp-mcp'), $stats['total_size_formatted']); ?></p>
            <?php if ($stats['oldest_backup']) : ?>
                <p><?php printf(__('Oldest Backup: %s', 'wp-mcp'), date_i18n(get_option('date_format'), $stats['oldest_backup'])); ?></p>
            <?php endif; ?>
            
            <form method="post" style="margin-top: 20px;">
                <?php wp_nonce_field('mcp_cleanup_backups'); ?>
                <input type="submit" name="cleanup_backups" class="button" 
                       value="<?php esc_attr_e('Clean Up Old Backups', 'wp-mcp'); ?>" />
            </form>
        </div>
        
        <div class="card">
            <h2><?php _e('Recent Backups', 'wp-mcp'); ?></h2>
            <?php if (empty($backups)) : ?>
                <p><?php _e('No backups found.', 'wp-mcp'); ?></p>
            <?php else : ?>
                <table class="widefat">
                    <thead>
                        <tr>
                            <th><?php _e('Date', 'wp-mcp'); ?></th>
                            <th><?php _e('Type', 'wp-mcp'); ?></th>
                            <th><?php _e('Original File', 'wp-mcp'); ?></th>
                            <th><?php _e('User', 'wp-mcp'); ?></th>
                            <th><?php _e('Actions', 'wp-mcp'); ?></th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php 
                        $count = 0;
                        foreach ($backups as $backup) : 
                            if ($count++ >= 20) break; // Show only recent 20
                            $user = get_userdata($backup['user_id']);
                        ?>
                            <tr>
                                <td><?php echo date_i18n(get_option('date_format') . ' ' . get_option('time_format'), $backup['timestamp']); ?></td>
                                <td><?php echo esc_html($backup['type']); ?></td>
                                <td><?php echo esc_html(basename($backup['original_path'])); ?></td>
                                <td><?php echo $user ? esc_html($user->display_name) : __('Unknown', 'wp-mcp'); ?></td>
                                <td>
                                    <form method="post" style="display: inline;">
                                        <?php wp_nonce_field('mcp_restore_backup'); ?>
                                        <input type="hidden" name="backup_path" value="<?php echo esc_attr($backup['backup_path']); ?>" />
                                        <input type="submit" name="restore_backup" class="button button-small" 
                                               value="<?php esc_attr_e('Restore', 'wp-mcp'); ?>"
                                               onclick="return confirm('<?php esc_attr_e('Are you sure you want to restore this backup?', 'wp-mcp'); ?>');" />
                                    </form>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php endif; ?>
        </div>
    </div>
    <?php
}
