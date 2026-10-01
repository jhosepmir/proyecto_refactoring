"""config.py - Reemplazo unificado de los modulos *_config.py.

Cada seccion (api, ui, cache, debug, ...) replica el comportamiento generico
de los 88 archivos *_config.py originales: variables globales, dicts "x_config"
y funciones load/save/get/set/reset/export/import/validate/backup/restore.

En lugar de un archivo por seccion con ~150 lineas de codigo duplicado, una
clase ConfigSection parametrizada con (nombre, archivo, defaults) cubre todo.

Uso:
    import config
    config.get("ui", "theme")
    config.set("ui", "theme", "light")
    config.section("api").get("omdb")
    config.validate("debug")
    config.backup("ui")
"""
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class ConfigSection:
    """Seccion de configuracion persistida en un archivo JSON."""

    def __init__(self, name, filename, defaults):
        self.name = name
        self.filename = filename
        self.defaults = dict(defaults)
        self.data = {}
        self._path = os.path.join(BASE_DIR, filename)
        self.load()

    def _full_path(self, filename):
        if os.path.isabs(filename) or os.path.dirname(filename):
            return filename
        return os.path.join(BASE_DIR, filename)

    def load(self):
        if os.path.exists(self._path):
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    self.data = loaded
                    return
            except (OSError, json.JSONDecodeError):
                pass
        self.data = dict(self.defaults)

    def save(self):
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def get_all(self):
        return dict(self.data)

    def reset(self):
        self.data = dict(self.defaults)
        self.save()

    def clear(self):
        self.data = {}
        self.save()

    def export(self, filename):
        path = self._full_path(filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    def import_from(self, filename):
        path = self._full_path(filename)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    self.data = loaded
                    self.save()
                    return True
            except (OSError, json.JSONDecodeError):
                return False
        return False

    def validate(self):
        """Valida tipos frente a los defaults. Devuelve lista de errores."""
        errors = []
        for key, default in self.defaults.items():
            if key in self.data:
                value = self.data[key]
                if isinstance(default, bool) and not isinstance(value, bool):
                    errors.append(f"{key} must be boolean")
                elif isinstance(default, int) and not isinstance(value, (int, float)):
                    errors.append(f"{key} must be integer")
                elif isinstance(default, list) and not isinstance(value, list):
                    errors.append(f"{key} must be list")
                elif isinstance(default, dict) and not isinstance(value, dict):
                    errors.append(f"{key} must be dict")
        return errors

    def backup(self):
        backup_name = f"{self.name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.export(backup_name)
        return backup_name

    def restore(self, backup_name):
        return self.import_from(backup_name)

    def summary(self):
        return dict(self.data)

    def is_enabled(self, key, default=False):
        return bool(self.data.get(key, default))

    def enable(self, key):
        self.set(key, True)

    def disable(self, key):
        self.set(key, False)

    def toggle(self, key):
        self.data[key] = not self.data.get(key, True)
        self.save()

    def __repr__(self):
        return "ConfigSection({!r}, file={!r})".format(self.name, self.filename)


class ConfigManager:
    """Registro de secciones de configuracion."""

    def __init__(self, registry):
        self._sections = {}
        for name, spec in registry.items():
            self._sections[name] = ConfigSection(name, spec["filename"], spec["defaults"])

    def section(self, name):
        if name not in self._sections:
            raise KeyError(f"Seccion de configuracion desconocida: {name!r}")
        return self._sections[name]

    def __getitem__(self, name):
        return self.section(name)

    def __contains__(self, name):
        return name in self._sections

    def sections(self):
        return sorted(self._sections)

    def get(self, name, key, default=None):
        return self.section(name).get(key, default)

    def set(self, name, key, value):
        self.section(name).set(key, value)

    def get_all(self, name):
        return self.section(name).get_all()

    def reset(self, name):
        return self.section(name).reset()

    def reset_all(self):
        for section in self._sections.values():
            section.reset()

    def validate(self, name):
        return self.section(name).validate()

    def backup(self, name):
        return self.section(name).backup()

    def restore(self, name, backup_name):
        return self.section(name).restore(backup_name)

    def summary(self, name):
        return self.section(name).summary()

    def summary_all(self):
        return {name: s.summary() for name, s in self._sections.items()}


REGISTRY = {
    'accessibility_config': {
        "filename": 'accessibility_config.json',
        "defaults": {'high_contrast': False, 'large_text': False, 'screen_reader': False, 'keyboard_navigation': True},
    },
    'api_auth_config': {
        "filename": 'api_auth_config.json',
        "defaults": {'enabled': False, 'auth_type': 'api_key', 'header_name': 'X-API-Key', 'token_expiry': 3600},
    },
    'api_bulkhead_config': {
        "filename": 'api_bulkhead_config.json',
        "defaults": {'enabled': True, 'max_concurrent_calls': 10, 'max_wait_time': 5000, 'timeout': 30000},
    },
    'api_cache_alerting_config': {
        "filename": 'api_cache_alerting_config.json',
        "defaults": {'enabled': True,
 'high_hit_rate_threshold': 0.9,
 'low_hit_rate_threshold': 0.1,
 'alert_cooldown': 300},
    },
    'api_cache_analytics_config': {
        "filename": 'api_cache_analytics_config.json',
        "defaults": {'enabled': True, 'track_performance': True, 'track_usage_patterns': True, 'generate_reports': True},
    },
    'api_cache_architecture_config': {
        "filename": 'api_cache_architecture_config.json',
        "defaults": {'cache_type': 'in-memory', 'persistence': False, 'clustering': False, 'eviction_strategy': 'lru'},
    },
    'api_cache_best_practices_config': {
        "filename": 'api_cache_best_practices_config.json',
        "defaults": {'enforce_naming_conventions': True,
 'require_documentation': True,
 'validate_configurations': True,
 'enforce_security_policies': True},
    },
    'api_cache_cleanup_config': {
        "filename": 'api_cache_cleanup_config.json',
        "defaults": {'enabled': True, 'cleanup_interval': 3600, 'max_cache_size_mb': 100, 'eviction_policy': 'lru'},
    },
    'api_cache_collaboration_config': {
        "filename": 'api_cache_collaboration_config.json',
        "defaults": {'enabled': True,
 'shared_cache': False,
 'cross_team_caching': False,
 'collaborative_optimization': True},
    },
    'api_cache_compliance_config': {
        "filename": 'api_cache_compliance_config.json',
        "defaults": {'gdpr_compliance': True,
 'data_retention_policy': 'standard',
 'audit_logging': True,
 'data_anonymization': False},
    },
    'api_cache_compression_config': {
        "filename": 'api_cache_compression_config.json',
        "defaults": {'enabled': True, 'algorithm': 'gzip', 'min_size_bytes': 1024, 'compression_level': 6},
    },
    'api_cache_config': {
        "filename": 'api_cache_config.json',
        "defaults": {'enable_api_cache': True,
 'api_cache_size_mb': 50,
 'api_cache_expiry_hours': 12,
 'cache_responses': True},
    },
    'api_cache_debug_config': {
        "filename": 'api_cache_debug_config.json',
        "defaults": {'enabled': False, 'verbose_logging': True, 'trace_requests': True, 'dump_cache_state': False},
    },
    'api_cache_deprecation_config': {
        "filename": 'api_cache_deprecation_config.json',
        "defaults": {'enabled': True,
 'deprecation_warnings': True,
 'auto_remove_expired': True,
 'grace_period_days': 30},
    },
    'api_cache_deprecation_schedule_config': {
        "filename": 'api_cache_deprecation_schedule_config.json',
        "defaults": {'auto_deprecate': True,
 'deprecation_announcement_days': 30,
 'grace_period_days': 90,
 'auto_remove_after_grace': True},
    },
    'api_cache_disaster_recovery_config': {
        "filename": 'api_cache_disaster_recovery_config.json',
        "defaults": {'enabled': False,
 'backup_frequency': 3600,
 'retention_period_days': 7,
 'geographic_redundancy': False},
    },
    'api_cache_distribution_config': {
        "filename": 'api_cache_distribution_config.json',
        "defaults": {'enabled': False,
 'distribution_strategy': 'consistent-hashing',
 'replication_factor': 3,
 'sync_interval': 60},
    },
    'api_cache_documentation_config': {
        "filename": 'api_cache_documentation_config.json',
        "defaults": {'enabled': True, 'auto_generate_docs': True, 'include_examples': True, 'api_reference': True},
    },
    'api_cache_evolution_config': {
        "filename": 'api_cache_evolution_config.json',
        "defaults": {'version': '1.0.0',
 'migration_strategy': 'backward-compatible',
 'deprecation_policy': 'grace-period',
 'compatibility_mode': True},
    },
    'api_cache_failover_config': {
        "filename": 'api_cache_failover_config.json',
        "defaults": {'enabled': True, 'fallback_to_disk': True, 'fallback_to_memory': True, 'auto_recovery': True},
    },
    'api_cache_future_config': {
        "filename": 'api_cache_future_config.json',
        "defaults": {'version': '2.0.0',
 'roadmap': ['ai-powered-caching', 'edge-caching', 'real-time-sync'],
 'beta_features': ['quantum-caching', 'neural-caching'],
 'research_areas': ['predictive-algorithms', 'self-healing-cache']},
    },
    'api_cache_governance_config': {
        "filename": 'api_cache_governance_config.json',
        "defaults": {'enabled': True, 'policy_enforcement': True, 'cache quotas': True, 'usage limits': True},
    },
    'api_cache_innovation_config': {
        "filename": 'api_cache_innovation_config.json',
        "defaults": {'enabled': True,
 'experimental_features': False,
 'research_mode': False,
 'innovation_pipeline': True},
    },
    'api_cache_integration_config': {
        "filename": 'api_cache_integration_config.json',
        "defaults": {'enabled': True,
 'integration_points': ['search', 'details', 'popular'],
 'fallback_strategy': 'pass-through',
 'error_handling': 'graceful'},
    },
    'api_cache_intelligence_config': {
        "filename": 'api_cache_intelligence_config.json',
        "defaults": {'enabled': True, 'predictive_caching': False, 'adaptive_ttl': False, 'machine_learning': False},
    },
    'api_cache_invalidation_config': {
        "filename": 'api_cache_invalidation_config.json',
        "defaults": {'enabled': True,
 'strategy': 'time-based',
 'invalidate_on_error': True,
 'invalidate_on_write': False},
    },
    'api_cache_legacy_config': {
        "filename": 'api_cache_legacy_config.json',
        "defaults": {'legacy_mode': True,
 'backward_compatibility': True,
 'deprecated_features': ['old-cache-format', 'v1-api-support'],
 'migration_required': False},
    },
    'api_cache_lifecycle_config': {
        "filename": 'api_cache_lifecycle_config.json',
        "defaults": {'enabled': True, 'ttl_enabled': True, 'max_idle_time': 3600, 'max_lifetime': 86400},
    },
    'api_cache_load_testing_config': {
        "filename": 'api_cache_load_testing_config.json',
        "defaults": {'enabled': False, 'max_concurrent_users': 100, 'ramp_up_period': 60, 'test_duration': 300},
    },
    'api_cache_mentoring_config': {
        "filename": 'api_cache_mentoring_config.json',
        "defaults": {'enabled': True, 'peer_review': True, 'code_review': True, 'best_practices_sharing': True},
    },
    'api_cache_metrics_config': {
        "filename": 'api_cache_metrics_config.json',
        "defaults": {'enabled': True, 'track_hit_miss_ratio': True, 'track_latency': True, 'track_size_evictions': True},
    },
    'api_cache_migration_config': {
        "filename": 'api_cache_migration_config.json',
        "defaults": {'enabled': False,
 'migration_strategy': 'gradual',
 'rollback_enabled': True,
 'data_validation': True},
    },
    'api_cache_migration_schedule_config': {
        "filename": 'api_cache_migration_schedule_config.json',
        "defaults": {'scheduled_migration': False,
 'migration_window': 'maintenance-hours',
 'auto_rollback': True,
 'notification_before_migration': True},
    },
    'api_cache_monitoring_config': {
        "filename": 'api_cache_monitoring_config.json',
        "defaults": {'enabled': True, 'track_hit_rate': True, 'track_size': True, 'alert_on_high_usage': True},
    },
    'api_cache_observability_config': {
        "filename": 'api_cache_observability_config.json',
        "defaults": {'enabled': True, 'metrics_collection': True, 'distributed_tracing': False, 'health_checks': True},
    },
    'api_cache_performance_config': {
        "filename": 'api_cache_performance_config.json',
        "defaults": {'optimize_for_read': True,
 'optimize_for_write': False,
 'batch_operations': True,
 'async_operations': False},
    },
    'api_cache_performance_testing_config': {
        "filename": 'api_cache_performance_testing_config.json',
        "defaults": {'enabled': False, 'benchmark_iterations': 1000, 'concurrent_clients': 10, 'measure_latency': True},
    },
    'api_cache_preloading_config': {
        "filename": 'api_cache_preloading_config.json',
        "defaults": {'enabled': False, 'preload_on_startup': True, 'preload_interval': 600, 'max_preload_items': 50},
    },
    'api_cache_recommendations_config': {
        "filename": 'api_cache_recommendations_config.json',
        "defaults": {'enabled': True,
 'auto_optimize': False,
 'suggest_ttl_adjustments': True,
 'suggest_cache_size': True},
    },
    'api_cache_recovery_config': {
        "filename": 'api_cache_recovery_config.json',
        "defaults": {'enabled': True,
 'auto_recovery': True,
 'recovery_strategy': 'last-known-good',
 'max_recovery_attempts': 3},
    },
    'api_cache_reporting_config': {
        "filename": 'api_cache_reporting_config.json',
        "defaults": {'enabled': True, 'report_frequency': 'daily', 'include_charts': True, 'export_format': 'json'},
    },
    'api_cache_resilience_testing_config': {
        "filename": 'api_cache_resilience_testing_config.json',
        "defaults": {'enabled': False, 'fault_injection': True, 'chaos_engineering': False, 'recovery_scenarios': True},
    },
    'api_cache_scalability_config': {
        "filename": 'api_cache_scalability_config.json',
        "defaults": {'enabled': True, 'auto_scaling': True, 'scale_up_threshold': 0.8, 'scale_down_threshold': 0.2},
    },
    'api_cache_security_config': {
        "filename": 'api_cache_security_config.json',
        "defaults": {'encrypt_cache': False,
 'validate_integrity': True,
 'secure_deletion': False,
 'access_control': False},
    },
    'api_cache_security_testing_config': {
        "filename": 'api_cache_security_testing_config.json',
        "defaults": {'enabled': False,
 'penetration_testing': False,
 'vulnerability_scanning': True,
 'security_audit': True},
    },
    'api_cache_serialization_config': {
        "filename": 'api_cache_serialization_config.json',
        "defaults": {'format': 'json', 'pretty_print': False, 'include_metadata': True, 'encoding': 'utf-8'},
    },
    'api_cache_stress_testing_config': {
        "filename": 'api_cache_stress_testing_config.json',
        "defaults": {'enabled': False, 'stress_level': 'high', 'recovery_timeout': 60, 'monitor_resources': True},
    },
    'api_cache_testing_config': {
        "filename": 'api_cache_testing_config.json',
        "defaults": {'enabled': False, 'mock_cache': True, 'test_isolation': True, 'verbose_output': True},
    },
    'api_cache_training_config': {
        "filename": 'api_cache_training_config.json',
        "defaults": {'enabled': True,
 'interactive_mode': True,
 'progress_tracking': True,
 'certification_enabled': False},
    },
    'api_cache_validation_config': {
        "filename": 'api_cache_validation_config.json',
        "defaults": {'enabled': True, 'validate_on_read': True, 'validate_checksum': False, 'strict_validation': False},
    },
    'api_cache_warming_config': {
        "filename": 'api_cache_warming_config.json',
        "defaults": {'enabled': False,
 'warming_interval': 300,
 'warming_strategy': 'predictive',
 'max_warming_items': 100},
    },
    'api_caching_strategy_config': {
        "filename": 'api_caching_strategy_config.json',
        "defaults": {'strategy': 'time-based', 'invalidate_on_error': True, 'pre_fetch': False, 'cache_warming': False},
    },
    'api_circuit_breaker_config': {
        "filename": 'api_circuit_breaker_config.json',
        "defaults": {'enabled': True, 'failure_threshold': 5, 'recovery_timeout': 30, 'half_open_max_calls': 3},
    },
    'api_config': {
        "filename": 'api_config.json',
        "defaults": {'omdb': {'url': 'http://www.omdbapi.com/', 'key': '', 'timeout': 30},
 'tvmaze': {'url': 'http://api.tvmaze.com', 'timeout': 30}},
    },
    'api_debug_config': {
        "filename": 'api_debug_config.json',
        "defaults": {'log_api_requests': True,
 'log_api_responses': True,
 'log_api_errors': True,
 'show_api_timing': True},
    },
    'api_degradation_config': {
        "filename": 'api_degradation_config.json',
        "defaults": {'enabled': True,
 'degrade_after_failures': 3,
 'recovery_after successes': 5,
 'degraded_response_time_ms': 1000},
    },
    'api_error_handling_config': {
        "filename": 'api_error_handling_config.json',
        "defaults": {'log_errors': True,
 'show_user_errors': True,
 'error_message_format': 'simple',
 'include_stack_trace': False},
    },
    'api_failover_config': {
        "filename": 'api_failover_config.json',
        "defaults": {'enabled': True, 'fallback_url': '', 'health_check_interval': 60, 'auto_switch': True},
    },
    'api_logging_config': {
        "filename": 'api_logging_config.json',
        "defaults": {'enabled': True, 'log_file': 'api.log', 'log_level': 'DEBUG', 'max_size_mb': 10},
    },
    'api_monitoring_config': {
        "filename": 'api_monitoring_config.json',
        "defaults": {'enabled': True,
 'track_response_times': True,
 'track_error_rates': True,
 'alert_threshold_ms': 5000},
    },
    'api_performance_config': {
        "filename": 'api_performance_config.json',
        "defaults": {'enable_compression': True,
 'enable_keep_alive': True,
 'connection_pool_size': 10,
 'max_connections': 100},
    },
    'api_rate_limit_config': {
        "filename": 'api_rate_limit_config.json',
        "defaults": {'omdb_requests_per_minute': 10,
 'tvmaze_requests_per_minute': 20,
 'enable_rate_limiting': True,
 'rate_limit_window': 60},
    },
    'api_rate_limiter_config': {
        "filename": 'api_rate_limiter_config.json',
        "defaults": {'enabled': True, 'algorithm': 'token-bucket', 'bucket_size': 10, 'refill_rate': 1},
    },
    'api_retry_config': {
        "filename": 'api_retry_config.json',
        "defaults": {'max_retries': 3, 'retry_delay': 1, 'exponential_backoff': True, 'max_retry_delay': 30},
    },
    'api_security_config': {
        "filename": 'api_security_config.json',
        "defaults": {'verify_ssl': True, 'allow_redirects': True, 'max_redirects': 5, 'user_agent': 'MovieExplorer/1.0'},
    },
    'api_testing_config': {
        "filename": 'api_testing_config.json',
        "defaults": {'enabled': False, 'mock_responses': True, 'test_timeout': 5, 'verbose_output': True},
    },
    'api_timeout_config': {
        "filename": 'api_timeout_config.json',
        "defaults": {'omdb_timeout': 30, 'tvmaze_timeout': 30, 'default_timeout': 30, 'connect_timeout': 10},
    },
    'api_timeout_retry_config': {
        "filename": 'api_timeout_retry_config.json',
        "defaults": {'connect_timeout': 10, 'read_timeout': 30, 'write_timeout': 30, 'retry_on_timeout': True},
    },
    'backup_config': {
        "filename": 'backup_config.json',
        "defaults": {'enabled': True,
 'interval_hours': 24,
 'max_backups': 10,
 'backup_dir': 'backups',
 'compress': False},
    },
    'cache_config': {
        "filename": 'cache_config.json',
        "defaults": {'enabled': True,
 'expiry_hours': 24,
 'max_size_mb': 100,
 'storage_type': 'file',
 'cleanup_interval': 3600},
    },
    'cache_expiry_config': {
        "filename": 'cache_expiry_config.json',
        "defaults": {'movie_expiry_hours': 24,
 'series_expiry_hours': 48,
 'search_expiry_hours': 12,
 'default_expiry_hours': 24},
    },
    'database_config': {
        "filename": 'database_config.json',
        "defaults": {'type': 'json', 'path': 'data', 'backup_enabled': True, 'max_backups': 10},
    },
    'debug_config': {
        "filename": 'debug_config.json',
        "defaults": {'enabled': True, 'verbose': True, 'show_errors': True, 'log_api_calls': True, 'show_timing': True},
    },
    'display_config': {
        "filename": 'display_config.json',
        "defaults": {'theme': 'dark', 'font_size': 14, 'show_icons': True, 'animations': True, 'compact_mode': False},
    },
    'email_config': {
        "filename": 'email_config.json',
        "defaults": {'smtp_server': 'smtp.gmail.com',
 'smtp_port': 587,
 'use_tls': True,
 'sender_email': '',
 'sender_password': ''},
    },
    'language_config': {
        "filename": 'language_config.json',
        "defaults": {'current': 'es', 'available': ['es', 'en', 'pt'], 'fallback': 'en'},
    },
    'log_config': {
        "filename": 'log_config.json',
        "defaults": {'enabled': True, 'level': 'DEBUG', 'file': 'app.log', 'max_size_mb': 10, 'backup_count': 5},
    },
    'maintenance_config': {
        "filename": 'maintenance_config.json',
        "defaults": {'enabled': False,
 'message': 'Sistema en mantenimiento',
 'estimated_time': '1 hora',
 'contact': 'admin@example.com'},
    },
    'network_config': {
        "filename": 'network_config.json',
        "defaults": {'timeout': 30,
 'max_retries': 3,
 'retry_delay': 1,
 'verify_ssl': True,
 'user_agent': 'MovieExplorer/1.0'},
    },
    'notification_config': {
        "filename": 'notification_config.json',
        "defaults": {'enabled': True, 'sound': True, 'desktop': True, 'email': False, 'max_notifications': 100},
    },
    'performance_config': {
        "filename": 'performance_config.json',
        "defaults": {'cache_size_mb': 100,
 'max_concurrent_requests': 5,
 'connection_pool_size': 10,
 'enable_compression': True},
    },
    'privacy_config': {
        "filename": 'privacy_config.json',
        "defaults": {'analytics_enabled': True,
 'crash_reporting': True,
 'personalization': True,
 'data_retention_days': 30},
    },
    'proxy_config': {
        "filename": 'proxy_config.json',
        "defaults": {'enabled': False, 'host': '', 'port': 8080, 'username': '', 'password': ''},
    },
    'search_config': {
        "filename": 'search_config.json',
        "defaults": {'max_results': 10,
 'enable_fuzzy': True,
 'min_score': 0.5,
 'boost_popularity': True,
 'cache_results': True},
    },
    'security_config': {
        "filename": 'security_config.json',
        "defaults": {'max_login_attempts': 5,
 'lockout_duration': 300,
 'password_min_length': 6,
 'require_special_chars': False,
 'session_timeout': 3600},
    },
    'storage_config': {
        "filename": 'storage_config.json',
        "defaults": {'data_dir': 'data', 'cache_dir': 'cache', 'backup_dir': 'backups', 'max_storage_mb': 1000},
    },
    'theme_config': {
        "filename": 'theme_config.json',
        "defaults": {'name': 'dark',
 'primary_color': '#007bff',
 'secondary_color': '#6c757d',
 'background_color': '#1a1a1a',
 'text_color': '#ffffff'},
    },
    'ui_config': {
        "filename": 'ui_config.json',
        "defaults": {'theme': 'dark',
 'language': 'es',
 'items_per_page': 10,
 'show_posters': True,
 'animations': True,
 'font_size': 14,
 'color_scheme': 'default'},
    },
}


manager = ConfigManager(REGISTRY)


def section(name):
    """Devuelve la ConfigSection correspondiente a una seccion."""
    return manager.section(name)


def sections():
    """Lista de nombres de secciones disponibles."""
    return manager.sections()


def get(name, key, default=None):
    """Obtiene una clave de una seccion."""
    return manager.get(name, key, default)


def set(name, key, value):
    """Establece una clave de una seccion y persiste."""
    manager.set(name, key, value)


def get_all(name):
    """Devuelve copia de todos los valores de una seccion."""
    return manager.get_all(name)


def reset(name):
    """Restaura los defaults de una seccion."""
    manager.reset(name)


def reset_all():
    """Restaura los defaults de todas las secciones."""
    manager.reset_all()


def validate(name):
    """Valida tipos de una seccion. Devuelve lista de errores."""
    return manager.validate(name)


def backup(name):
    """Copia de seguridad en JSON con timestamp."""
    return manager.backup(name)


def restore(name, backup_name):
    """Restaura una seccion desde un backup."""
    return manager.restore(name, backup_name)


def summary(name):
    """Resumen (copia) de una seccion."""
    return manager.summary(name)


# Configuracion de ejecucion (mutable en runtime desde el menu opcion 11).
# Compartida por la capa api (cliente HTTP) y la capa ui (menu) sin violar la
# direccion de dependencias.
#
# Las claves de API se leen de variables de entorno (SEGURIDAD). El fallback
# "trilogy" es la clave publica DEMO de OMDb (no sensible) para que el proyecto
# funcione sin red; cualquier despliegue real debe setear OMDB_API_KEY.
CONFIG = {
    "debug": get("debug_config", "enabled"),
    "verbose": get("debug_config", "verbose"),
    "timeout": get("network_config", "timeout"),
    "max_retries": get("network_config", "max_retries"),
    "api_key_omdb": os.getenv("OMDB_API_KEY", "trilogy"),
    "api_key_tmdb": os.getenv("TMDB_API_KEY", ""),
}
