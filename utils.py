from models import AuditLog, Permission
from app import db
from flask import request
from datetime import datetime
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

def log_audit_event(user_id, action, target_type=None, target_id=None, details=None):
    """Log an audit event"""
    try:
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
            ip_address=request.remote_addr if request else None
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error logging audit event: {e}")

def generate_pdf_report(title, group, members):
    """Generate a PDF report for group membership"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = styles['Title']
    title_para = Paragraph(title, title_style)
    story.append(title_para)
    story.append(Spacer(1, 0.2*inch))
    
    # Group information
    group_info = f"""
    <b>Group Name:</b> {group.name}<br/>
    <b>Email:</b> {group.email}<br/>
    <b>Description:</b> {group.description or 'No description'}<br/>
    <b>Total Members:</b> {len(members)}<br/>
    <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    group_para = Paragraph(group_info, styles['Normal'])
    story.append(group_para)
    story.append(Spacer(1, 0.3*inch))
    
    # Members table
    if members:
        # Table header
        data = [['Name', 'Email', 'Department', 'Location', 'Phone']]
        
        # Add member data
        for member in members:
            data.append([
                member.display_name or '',
                member.email or '',
                member.department or '',
                member.location or '',
                member.phone or ''
            ])
        
        # Create table
        table = Table(data, colWidths=[2*inch, 2.5*inch, 1.5*inch, 1.5*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(table)
    else:
        no_members_para = Paragraph("No members found in this group.", styles['Normal'])
        story.append(no_members_para)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def get_user_permissions(user):
    """Get a user's effective permissions"""
    permissions = []
    
    if user.is_admin:
        permissions.append('full_admin')
    
    if user.can_manage_groups:
        permissions.append('manage_groups')
    
    # Add any specific permissions from Permission model
    specific_perms = Permission.query.filter_by(user_id=user.id).all()
    for perm in specific_perms:
        permissions.append(perm.permission_type)
    
    return list(set(permissions))

def format_datetime(dt):
    """Format datetime for display"""
    if not dt:
        return 'Never'
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def truncate_text(text, length=50):
    """Truncate text to specified length"""
    if not text:
        return ''
    return text[:length] + '...' if len(text) > length else text
