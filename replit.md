# Distribution Group Management System

## Overview

This is a Flask-based web application for managing distribution groups and user membership within an organization. The system provides a corporate-style interface for administrators and users to manage email distribution groups, track membership, generate reports, and maintain audit logs. It simulates Windows authentication for enterprise environments and includes role-based access control with different permission levels for administrators, group managers, and regular users.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web framework with Blueprint-based modular design
- **Database ORM**: SQLAlchemy with Flask-SQLAlchemy extension using DeclarativeBase
- **Authentication**: Flask-Login for session management with simulated Windows authentication
- **Database**: SQLite for development (configurable via DATABASE_URL environment variable)
- **Connection Management**: Connection pooling with pool recycling and pre-ping health checks
- **Proxy Support**: ProxyFix middleware for deployment behind reverse proxies

### Database Schema Design
- **User Model**: Stores user information including username, email, display name, department, location, role, and permission flags
- **DistributionGroup Model**: Manages group information with name, description, email address, and metadata
- **Many-to-Many Relationship**: group_members association table linking users to groups
- **Permission Model**: Role-based access control system
- **AuditLog Model**: Tracks all system activities for compliance and monitoring

### Authentication & Authorization
- **Simulated Windows Auth**: Mock authentication system that creates default users for different roles
- **Role-Based Access**: Three-tier permission system (admin, group manager, regular user)
- **Session Management**: Flask-Login handles user sessions with configurable login views
- **Permission Decorators**: Custom decorators for protecting routes based on user roles

### Frontend Architecture
- **Template Engine**: Jinja2 with Bootstrap 5 for responsive design
- **CSS Framework**: Custom Microsoft-inspired design system with CSS variables
- **JavaScript**: jQuery-based interactive components with DataTables integration
- **Component Structure**: Modular template inheritance with reusable components

### Reporting System
- **PDF Generation**: ReportLab library for creating detailed membership reports
- **Export Functionality**: Multiple export formats for group data
- **Audit Trail**: Comprehensive logging of all user actions and system changes

## External Dependencies

### Frontend Libraries
- **Bootstrap 5.3.0**: UI framework for responsive design and components
- **Bootstrap Icons**: Icon library for consistent visual elements
- **DataTables 1.13.4**: Enhanced table functionality with sorting, searching, and pagination
- **jQuery**: JavaScript framework for DOM manipulation and AJAX requests

### Python Packages
- **Flask**: Core web framework
- **Flask-SQLAlchemy**: Database ORM integration
- **Flask-Login**: User session management
- **Werkzeug**: WSGI utilities and security helpers
- **ReportLab**: PDF generation for reports

### Development Tools
- **SQLite**: Default development database (production-ready for PostgreSQL via DATABASE_URL)
- **Logging**: Python's built-in logging module configured for debugging

### Configuration Management
- **Environment Variables**: SESSION_SECRET for session security, DATABASE_URL for database configuration
- **Development Defaults**: Fallback configurations for local development