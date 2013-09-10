AGS_ADMIN_PATH_PATTERNS = {
    'generate_token': "%(admin_root)s/generateToken",
    'list_services': "%(admin_root)s/services%(folder)",
    'create_service': "%(admin_root)s/services/createService",
    'get_service': "%(admin_root)s/services/%(service_path)s.%(service_type)s",
    'edit_service': "%(admin_root)s/services/%(service_path)s.%(service_type)s/edit",
    'get_service_item_info': "%(admin_root)s/services/%(service_path)s.%(service_type)s/iteminfo",
    'edit_service_item_info': "%(admin_root)s/services/%(service_path)s.%(service_type)s/iteminfo/edit",
    'get_service_status': "%(admin_root)s/services/%(service_path)s.(service_type)s/status",
    'start_service': "%(admin_root)s/services/%(service_path)s.%(service_type)s/start",
    'stop_service': "%(admin_root)s/services/%(service_path)s.%(service_type)s/stop",
    'delete_service': "%(admin_root)s/services/%(service_path)s.%(service_type)s/delete"
}