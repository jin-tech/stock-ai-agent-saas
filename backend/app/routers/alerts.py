from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.database import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertResponse, AlertListResponse, AlertUpdate

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new alert.
    
    This endpoint receives alert data from the frontend and saves it to the PostgreSQL database.
    """
    try:
        # Create new alert instance
        db_alert = Alert(
            symbol=alert_data.symbol.upper(),  # Normalize symbol to uppercase
            alert_type=alert_data.alert_type,
            condition=alert_data.condition,
            threshold_value=alert_data.threshold_value,
            message=alert_data.message,
            is_active=alert_data.is_active
        )
        
        # Add to database
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        
        return db_alert
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error occurred"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the alert"
        )


@router.get("/", response_model=AlertListResponse)
async def get_alerts(
    skip: int = 0,
    limit: int = 100,
    symbol: str = None,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve alerts with optional filtering.
    """
    query = db.query(Alert)
    
    # Apply filters
    if symbol:
        query = query.filter(Alert.symbol == symbol.upper())
    if is_active is not None:
        query = query.filter(Alert.is_active == is_active)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    alerts = query.offset(skip).limit(limit).all()
    
    return AlertListResponse(
        alerts=alerts,
        total=total,
        page=(skip // limit) + 1 if limit > 0 else 1,
        page_size=limit
    )


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """
    Get a specific alert by ID.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    return alert


@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_data: AlertUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing alert.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    # Update fields that are provided
    update_data = alert_data.model_dump(exclude_unset=True)
    if "symbol" in update_data:
        update_data["symbol"] = update_data["symbol"].upper()
    
    for field, value in update_data.items():
        setattr(alert, field, value)
    
    try:
        db.commit()
        db.refresh(alert)
        return alert
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the alert"
        )


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """
    Delete an alert.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    db.delete(alert)
    db.commit()
    return None