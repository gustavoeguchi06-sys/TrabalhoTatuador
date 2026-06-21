try:
    import pymysql
    pymysql.install_as_MySQLdb()
except Exception:
    # PyMySQL not installed or failed to initialize; fallback to builtin DB drivers
    pass
