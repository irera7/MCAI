"""
Model Comparison API Routes
مسیرهای API برای مقایسه مدل‌های مختلف

این API امکان مقایسه و تحلیل مدل‌های آموزش‌دیده را فراهم می‌کند
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

router = APIRouter(prefix="/api/comparison", tags=["comparison"])


# ============================================
# Helper Functions
# ============================================

def get_all_completed_projects() -> List[Dict[str, Any]]:
    """
    دریافت تمام پروژه‌های تکمیل شده
    
    Returns:
        لیست پروژه‌ها با اطلاعات training
    """
    projects_dir = Path("projects")
    if not projects_dir.exists():
        return []
    
    completed_projects = []
    
    for project_path in projects_dir.iterdir():
        if project_path.is_dir():
            project_file = project_path / "project.json"
            
            if project_file.exists():
                with open(project_file, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                    
                    # فقط پروژه‌های تکمیل شده
                    if info.get('status') == 'completed':
                        # خواندن training history
                        history_file = project_path / "training_history.json"
                        if history_file.exists():
                            with open(history_file, 'r', encoding='utf-8') as hf:
                                history = json.load(hf)
                        else:
                            history = {}
                        
                        completed_projects.append({
                            'project_id': info.get('id', project_path.name),
                            'project_name': info.get('name', 'Unknown'),
                            'model_architecture': info.get('model_architecture', 'Unknown'),
                            'modality': info.get('modality', 'image'),
                            'num_classes': info.get('num_classes', 0),
                            'best_accuracy': info.get('best_accuracy', 0.0),
                            'best_loss': info.get('best_loss', 0.0),
                            'total_epochs': info.get('total_epochs', 0),
                            'batch_size': info.get('batch_size', 32),
                            'learning_rate': info.get('learning_rate', 0.001),
                            'created_at': info.get('created_at', ''),
                            'training_duration': info.get('training_duration', 0.0),
                            'history': history
                        })
    
    return completed_projects


def get_project_details(project_id: str) -> Dict[str, Any]:
    """
    دریافت جزئیات کامل یک پروژه
    
    Args:
        project_id: شناسه پروژه
        
    Returns:
        اطلاعات کامل پروژه
    """
    project_dir = Path("projects") / project_id
    if not project_dir.exists():
        raise FileNotFoundError(f"Project not found: {project_id}")
    
    project_file = project_dir / "project.json"
    if not project_file.exists():
        raise FileNotFoundError(f"Project file not found: {project_id}")
    
    with open(project_file, 'r', encoding='utf-8') as f:
        info = json.load(f)
    
    # خواندن training history
    history_file = project_dir / "training_history.json"
    if history_file.exists():
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = {}
    
    return {
        **info,
        'history': history
    }


# ============================================
# API Endpoints
# ============================================

@router.get("/projects")
async def get_completed_projects():
    """
    دریافت لیست تمام پروژه‌های تکمیل شده برای مقایسه
    
    Returns:
        لیست پروژه‌ها
    """
    try:
        projects = get_all_completed_projects()
        
        # مرتب‌سازی بر اساس accuracy
        projects.sort(key=lambda x: x['best_accuracy'], reverse=True)
        
        return JSONResponse({
            'status': 'success',
            'projects': projects,
            'total': len(projects)
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"خطا در دریافت پروژه‌ها: {str(e)}"
        )


@router.post("/compare")
async def compare_projects(project_ids: List[str]):
    """
    مقایسه چند پروژه با یکدیگر
    
    Args:
        project_ids: لیست شناسه پروژه‌ها
        
    Returns:
        نتایج مقایسه
    """
    try:
        if len(project_ids) < 2:
            raise HTTPException(
                status_code=400,
                detail="حداقل 2 پروژه برای مقایسه نیاز است"
            )
        
        comparison_results = []
        
        for project_id in project_ids:
            try:
                details = get_project_details(project_id)
                comparison_results.append(details)
            except Exception as e:
                raise HTTPException(
                    status_code=404,
                    detail=f"پروژه {project_id} یافت نشد: {str(e)}"
                )
        
        # محاسبه آمار مقایسه
        stats = {
            'best_model': max(comparison_results, key=lambda x: x.get('best_accuracy', 0)),
            'fastest_training': min(comparison_results, key=lambda x: x.get('training_duration', float('inf'))),
            'average_accuracy': sum(p.get('best_accuracy', 0) for p in comparison_results) / len(comparison_results),
            'accuracy_std': 0.0  # محاسبه انحراف معیار
        }
        
        # محاسبه انحراف معیار
        import statistics
        accuracies = [p.get('best_accuracy', 0) for p in comparison_results]
        if len(accuracies) > 1:
            stats['accuracy_std'] = statistics.stdev(accuracies)
        
        return JSONResponse({
            'status': 'success',
            'comparison': comparison_results,
            'statistics': stats,
            'total_compared': len(comparison_results)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"خطا در مقایسه: {str(e)}"
        )


@router.get("/project/{project_id}/details")
async def get_project_comparison_details(project_id: str):
    """
    دریافت جزئیات کامل یک پروژه برای مقایسه
    
    Args:
        project_id: شناسه پروژه
        
    Returns:
        جزئیات کامل شامل history و metrics
    """
    try:
        details = get_project_details(project_id)
        
        return JSONResponse({
            'status': 'success',
            'project': details
        })
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"خطا در دریافت جزئیات: {str(e)}"
        )


@router.get("/export/csv")
async def export_comparison_csv(project_ids: str):
    """
    Export مقایسه به فرمت CSV
    
    Args:
        project_ids: لیست project IDs جدا شده با کاما (e.g. "id1,id2,id3")
        
    Returns:
        CSV file
    """
    try:
        from fastapi.responses import StreamingResponse
        import io
        import csv
        
        ids = project_ids.split(',')
        projects = []
        
        for pid in ids:
            pid = pid.strip()
            if pid:
                try:
                    details = get_project_details(pid)
                    projects.append(details)
                except:
                    pass
        
        if not projects:
            raise HTTPException(status_code=404, detail="No projects found")
        
        # ایجاد CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Project Name',
            'Model',
            'Modality',
            'Best Accuracy (%)',
            'Best Loss',
            'Total Epochs',
            'Batch Size',
            'Learning Rate',
            'Training Duration (s)',
            'Created At'
        ])
        
        # Rows
        for project in projects:
            writer.writerow([
                project.get('name', 'Unknown'),
                project.get('model_architecture', 'Unknown'),
                project.get('modality', 'image'),
                f"{project.get('best_accuracy', 0):.2f}",
                f"{project.get('best_loss', 0):.4f}",
                project.get('total_epochs', 0),
                project.get('batch_size', 32),
                project.get('learning_rate', 0.001),
                f"{project.get('training_duration', 0):.2f}",
                project.get('created_at', '')
            ])
        
        # Return CSV
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=model_comparison.csv"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"خطا در export: {str(e)}"
        )


@router.get("/statistics")
async def get_global_statistics():
    """
    دریافت آمار کلی تمام مدل‌های آموزش‌دیده
    
    Returns:
        آمار کلی
    """
    try:
        projects = get_all_completed_projects()
        
        if not projects:
            return JSONResponse({
                'status': 'success',
                'statistics': {
                    'total_projects': 0,
                    'average_accuracy': 0.0,
                    'best_accuracy': 0.0,
                    'total_training_time': 0.0,
                    'models_by_architecture': {},
                    'models_by_modality': {}
                }
            })
        
        # محاسبه آمار
        accuracies = [p['best_accuracy'] for p in projects]
        durations = [p['training_duration'] for p in projects]
        
        # گروه‌بندی بر اساس architecture
        by_arch = {}
        for p in projects:
            arch = p['model_architecture']
            if arch not in by_arch:
                by_arch[arch] = {'count': 0, 'avg_accuracy': 0.0}
            by_arch[arch]['count'] += 1
            by_arch[arch]['avg_accuracy'] += p['best_accuracy']
        
        for arch in by_arch:
            by_arch[arch]['avg_accuracy'] /= by_arch[arch]['count']
        
        # گروه‌بندی بر اساس modality
        by_mod = {}
        for p in projects:
            mod = p['modality']
            if mod not in by_mod:
                by_mod[mod] = {'count': 0, 'avg_accuracy': 0.0}
            by_mod[mod]['count'] += 1
            by_mod[mod]['avg_accuracy'] += p['best_accuracy']
        
        for mod in by_mod:
            by_mod[mod]['avg_accuracy'] /= by_mod[mod]['count']
        
        import statistics
        
        stats = {
            'total_projects': len(projects),
            'average_accuracy': statistics.mean(accuracies),
            'best_accuracy': max(accuracies),
            'worst_accuracy': min(accuracies),
            'std_accuracy': statistics.stdev(accuracies) if len(accuracies) > 1 else 0.0,
            'total_training_time': sum(durations),
            'average_training_time': statistics.mean(durations),
            'models_by_architecture': by_arch,
            'models_by_modality': by_mod
        }
        
        return JSONResponse({
            'status': 'success',
            'statistics': stats
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"خطا در محاسبه آمار: {str(e)}"
        )

