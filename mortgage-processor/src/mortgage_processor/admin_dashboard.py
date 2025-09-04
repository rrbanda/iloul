"""
Simple admin dashboard for viewing mortgage applications.
Provides web interface to track and manage applications.
"""

from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from datetime import datetime
import os

from .database import get_db_session, MortgageApplicationDB

# Create admin router
admin_router = APIRouter(prefix="/admin", tags=["admin"])

# Setup templates (create templates directory if needed)
template_dir = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(template_dir, exist_ok=True)
templates = Jinja2Templates(directory=template_dir)


@admin_router.get("/applications", response_class=HTMLResponse)
async def admin_applications_page(request: Request, status: Optional[str] = None):
    """Admin dashboard page to view all applications"""
    try:
        with get_db_session() as db:
            query = db.query(MortgageApplicationDB)
            
            # Apply status filter if provided
            if status:
                query = query.filter(MortgageApplicationDB.status == status)
            
            applications = query.order_by(
                MortgageApplicationDB.submitted_at.desc()
            ).limit(100).all()  # Limit to 100 most recent
            
            # Get unique statuses for filter dropdown
            all_statuses = db.query(MortgageApplicationDB.status).distinct().all()
            status_options = [s[0] for s in all_statuses if s[0]]
            
            return templates.TemplateResponse("admin_dashboard.html", {
                "request": request,
                "applications": applications,
                "current_status_filter": status,
                "status_options": status_options,
                "total_count": len(applications)
            })
            
    except Exception as e:
        # Return simple HTML error page
        return HTMLResponse(
            content=f"<h1>Error</h1><p>Failed to load applications: {str(e)}</p>",
            status_code=500
        )


@admin_router.get("/applications/{application_id}", response_class=HTMLResponse)
async def admin_application_detail(request: Request, application_id: str):
    """Detailed view of a specific application"""
    try:
        with get_db_session() as db:
            application = db.query(MortgageApplicationDB).filter(
                MortgageApplicationDB.application_id == application_id
            ).first()
            
            if not application:
                return HTMLResponse(
                    content="<h1>Not Found</h1><p>Application not found</p>",
                    status_code=404
                )
            
            return templates.TemplateResponse("application_detail.html", {
                "request": request,
                "application": application
            })
            
    except Exception as e:
        return HTMLResponse(
            content=f"<h1>Error</h1><p>Failed to load application: {str(e)}</p>",
            status_code=500
        )


@admin_router.post("/applications/{application_id}/update-status")
async def update_application_status_form(
    application_id: str,
    status: str = Form(...),
    notes: str = Form("")
):
    """Update application status via form submission"""
    try:
        with get_db_session() as db:
            application = db.query(MortgageApplicationDB).filter(
                MortgageApplicationDB.application_id == application_id
            ).first()
            
            if not application:
                raise HTTPException(status_code=404, detail="Application not found")
            
            # Update status
            application.status = status
            if notes:
                existing_notes = application.processing_notes or ""
                application.processing_notes = f"{existing_notes}\n[{datetime.now().isoformat()}] {notes}".strip()
            
            db.commit()
            
            # Redirect back to detail page
            return HTMLResponse(
                content=f'<script>window.location.href="/admin/applications/{application_id}"</script>',
                status_code=200
            )
            
    except Exception as e:
        return HTMLResponse(
            content=f"<h1>Error</h1><p>Failed to update application: {str(e)}</p>",
            status_code=500
        )


@admin_router.get("/", response_class=HTMLResponse)
async def admin_home(request: Request):
    """Admin dashboard home page with statistics"""
    try:
        with get_db_session() as db:
            # Get basic statistics
            total_applications = db.query(MortgageApplicationDB).count()
            submitted_count = db.query(MortgageApplicationDB).filter(
                MortgageApplicationDB.status == "submitted"
            ).count()
            incomplete_count = db.query(MortgageApplicationDB).filter(
                MortgageApplicationDB.status == "incomplete"
            ).count()
            
            # Get recent applications
            recent_applications = db.query(MortgageApplicationDB).order_by(
                MortgageApplicationDB.submitted_at.desc()
            ).limit(5).all()
            
            stats = {
                "total": total_applications,
                "submitted": submitted_count,
                "incomplete": incomplete_count,
                "recent": recent_applications
            }
            
            return templates.TemplateResponse("admin_home.html", {
                "request": request,
                "stats": stats
            })
            
    except Exception as e:
        return HTMLResponse(
            content=f"<h1>Error</h1><p>Failed to load dashboard: {str(e)}</p>",
            status_code=500
        )
