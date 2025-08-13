# Migration Notes for PaiNaiDee Backend v2.0

This document outlines the breaking changes and migration steps for upgrading from the previous version to PaiNaiDee Backend v2.0.

## 🚀 Major Changes

### Project Structure Restructuring

**Breaking Change**: The entire project structure has been reorganized from `src/` to `app/` directory layout.

**Before (v1.x)**:
```
src/
├── app.py
├── config.py
├── models/
├── routes/
├── services/
└── utils/
```

**After (v2.0)**:
```
app/
├── __init__.py (app factory)
├── config.py (enhanced)
├── extensions.py (new)
├── blueprints/api/
├── models/
├── services/
├── utils/
└── schemas/
```

**Migration Steps**:
1. Update all imports from `src.` to `app.`
2. Update deployment scripts to use `app` package
3. Update `FLASK_APP` environment variable from `src.app` to `run_new.py` or use the new app factory

### Configuration Changes

**Breaking Change**: Enhanced configuration system with new required variables.

**New Environment Variables**:
```env
# Search Configuration (new)
SEARCH_RANK_WEIGHTS={"popularity": 0.4, "freshness": 0.3, "similarity": 0.3}
MAX_NEARBY_RADIUS_KM=50
TRIGRAM_SIM_THRESHOLD=0.3
FEATURE_AUTOCOMPLETE=true
FEATURE_NEARBY=true

# Optional: Redis support
REDIS_URL=redis://localhost:6379/0

# Enhanced database config
DATABASE_URL=postgresql://user:pass@host:port/db  # Preferred over individual components
```

**Migration Steps**:
1. Update `.env` file with new variables (see `.env.example`)
2. Set `DATABASE_URL` for production environments
3. Configure search feature flags as needed

### Database Changes

**Breaking Change**: New migration system with Alembic.

**New Features**:
- Alembic-based database migrations
- Search indexes for improved performance
- PostgreSQL pg_trgm extension support

**Migration Steps**:
1. Install Flask-Migrate: `pip install Flask-Migrate==4.0.5`
2. Initialize migrations: `flask db init` (if not using provided migrations)
3. Run initial migration: `flask db upgrade`
4. For PostgreSQL: Ensure pg_trgm extension is available

### API Changes

**New Endpoints**:
- `GET /api/autocomplete?q={query}` - Autocomplete suggestions
- `GET /api/locations/nearby?lat={lat}&lng={lng}&radius={km}` - Nearby locations

**Enhanced Endpoints**:
- `GET /api/search` - Now supports similarity-based search with PostgreSQL trigram matching
- Improved search ranking and filtering

**No Breaking Changes**: All existing API endpoints maintain backward compatibility.

## 📦 Dependency Changes

**New Dependencies**:
- `Flask-Migrate>=4.0.5` - Database migrations
- `ruff` - Code linting and formatting
- `black` - Code formatting
- `isort` - Import sorting

**Installation**:
```bash
pip install -r requirements.txt
```

## 🔧 Development Workflow Changes

**New Tools**:
- **Ruff**: Fast Python linter and formatter
- **Pre-commit hooks**: Automated code quality checks
- **pyproject.toml**: Centralized tool configuration

**Setup**:
```bash
# Install development tools
pip install ruff black isort pre-commit

# Setup pre-commit hooks (optional)
pre-commit install

# Format code
ruff format app/
ruff check app/ --fix
```

## 🚨 Breaking Changes Summary

1. **Import paths**: All `src.*` imports must be changed to `app.*`
2. **App initialization**: Use new app factory pattern
3. **Database migrations**: Switch from manual scripts to Alembic
4. **Environment variables**: Add new search-related configuration
5. **Project structure**: Update deployment and development scripts

## 🔄 Migration Checklist

### For Developers

- [ ] Update local development environment
- [ ] Update imports in custom code
- [ ] Update IDE/editor configuration
- [ ] Run tests to ensure compatibility
- [ ] Update development scripts

### For DevOps/Deployment

- [ ] Update deployment scripts
- [ ] Update environment variables
- [ ] Run database migrations
- [ ] Update CI/CD pipelines
- [ ] Update monitoring and logging
- [ ] Test new search endpoints

### For Production

- [ ] **Backup database before migration**
- [ ] Update environment configuration
- [ ] Deploy new code with maintenance window
- [ ] Run `flask db upgrade` for database migrations
- [ ] Verify all endpoints are working
- [ ] Monitor performance with new search features

## 🆘 Rollback Plan

If issues occur during migration:

1. **Code rollback**: Revert to previous version tag
2. **Database rollback**: `flask db downgrade` (if needed)
3. **Configuration rollback**: Restore previous environment variables
4. **Monitoring**: Check logs and application metrics

## 📞 Support

If you encounter issues during migration:

1. Check the logs for specific error messages
2. Verify environment variable configuration
3. Ensure database connectivity and permissions
4. Test with SQLite first for development
5. Create an issue on GitHub for support

## 🎯 Benefits of Migration

After successful migration, you'll have:

- **Better search**: Similarity-based search with Thai/English support
- **Performance**: Optimized database indexes and queries
- **Developer experience**: Better code quality tools and project structure
- **Scalability**: Modern Flask patterns and configuration management
- **Maintainability**: Clear separation of concerns and better testing

---

**Version**: 2.0.0  
**Date**: December 2024  
**Migration Difficulty**: Medium  
**Estimated Migration Time**: 2-4 hours for development, 1-2 hours for production