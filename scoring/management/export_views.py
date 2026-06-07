from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.http import HttpResponse, JsonResponse
from .models import ExamPaper, ExamRecord, AnswerDetail, Class
import pandas as pd
from io import BytesIO
import logging

# 配置日志
logger = logging.getLogger(__name__)

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def export_report_view(request):
    # 导出报告
    print("!!! EXPORT REPORT VIEW CALLED - START !!!")  # 添加明显的打印语句
    print("!!! REQUEST METHOD:", request.method)
    print("!!! REQUEST PATH:", request.path)
    print("!!! REQUEST QUERY PARAMS:", request.query_params)
    print("!!! ALL REQUEST GET PARAMS:", request.GET)
    logger.info("Export report view called")
    params = request.query_params
    logger.info(f"Params: {params}")
    
    # 获取考试信息
    exam_id = params.get('exam_id', None)
    print(f"!!! EXAM ID: {exam_id}")
    logger.info(f"Exam ID: {exam_id}")
    if not exam_id:
        logger.warning("Missing exam_id parameter")
        print("!!! MISSING EXAM ID PARAMETER")
        return JsonResponse({'error': '缺少考试ID参数'}, status=400)
    
    exam_name = "未知考试"
    if exam_id:
        try:
            exam = ExamPaper.objects.get(number=exam_id)
            exam_name = exam.name
            logger.info(f"Found exam: {exam_name}")
            print(f"!!! FOUND EXAM: {exam_name}")
        except ExamPaper.DoesNotExist:
            logger.warning(f"Exam with ID {exam_id} not found")
            print(f"!!! EXAM {exam_id} NOT FOUND")
            pass
    
    # 获取班级筛选条件
    class_ids = params.getlist('class_ids', [])
    print(f"!!! CLASS IDS FROM GETLIST: {class_ids}")
    class_ids = [cid for cid in class_ids if cid]  # 移除空值
    if not class_ids:
        class_ids_str = params.get('class_ids', '')
        print(f"!!! CLASS IDS STR: {class_ids_str}")
        if class_ids_str:
            if isinstance(class_ids_str, str):
                class_ids = class_ids_str.split(',') if ',' in class_ids_str else [class_ids_str]
            else:
                class_ids = [str(class_ids_str)]
            # 移除空值
            class_ids = [cid for cid in class_ids if cid]
    
    logger.info(f"Class IDs: {class_ids}")
    print(f"!!! CLASS IDS: {class_ids}")
    
    # 获取报表类型和排序方式
    report_type = params.get('report_type', 'grade')  # 默认为成绩单
    sort_by = params.get('sort_by', 'class')  # 默认按班级排序
    print(f"!!! REPORT TYPE: {report_type}")
    print(f"!!! SORT BY: {sort_by}")
    
    # 获取真实的考试记录数据
    exam_records = ExamRecord.objects.filter(exam_paper__number=exam_id)
    print(f"!!! FOUND {exam_records.count()} EXAM RECORDS !!!")
    logger.info(f"Found {exam_records.count()} exam records")
    
    # 如果指定了班级，进行筛选
    if class_ids:
        # 将class_ids转换为整数列表
        try:
            class_ids_int = []
            for cid in class_ids:
                if isinstance(cid, str) and cid.isdigit():
                    class_ids_int.append(int(cid))
                elif isinstance(cid, int):
                    class_ids_int.append(cid)
            
            if class_ids_int:
                exam_records = exam_records.filter(user__class1__id__in=class_ids_int)
                logger.info(f"Filtered to {exam_records.count()} records after class filter")
                print(f"!!! FILTERED TO {exam_records.count()} RECORDS AFTER CLASS FILTER")
        except (ValueError, TypeError):
            logger.warning("Error converting class_ids to integers")
            print("!!! ERROR CONVERTING CLASS IDS TO INTEGERS")
            pass  # 如果转换失败，不进行班级筛选
    
    # 根据排序方式对记录进行排序
    if sort_by == 'score':
        exam_records = exam_records.order_by('-end_score')
    elif sort_by == 'studentId':
        exam_records = exam_records.order_by('user__id')
    else:  # 默认按班级排序
        # 处理可能为None的class1字段，避免排序时出错
        exam_records = exam_records.order_by('-end_score')
    
    # 准备数据列表
    report_data = []
    
    # 定义客观题类型常量（兼容多种命名格式）
    OBJECTIVE_TYPES = ['单项选择题', '多项选择题', '判断题', '单选题', '多选题']
    
    # 为每个考试记录计算详细成绩信息
    for record in exam_records:
        print(f"!!! PROCESSING RECORD {record.number} !!!")
        # 获取答题详情
        answer_details = AnswerDetail.objects.filter(record_id=record.number)
        print(f"!!! FOUND {answer_details.count()} ANSWER DETAILS FOR RECORD {record.number} !!!")
        
        # 计算客观题和主观题得分
        objective_score = 0
        subjective_score = 0
        
        for answer_detail in answer_details:
            # 根据 type1 字段判断题型
            if answer_detail.type1 in OBJECTIVE_TYPES:  # 客观题
                objective_score += answer_detail.score or 0
            else:  # 主观题
                subjective_score += answer_detail.score or 0
        
        # 修复总分计算：通过客观题和主观题得分之和计算总分，而不是直接使用record.end_score
        total_score = objective_score + subjective_score
        
        # 计算班级排名
        class_rank = 1
        if record.user and record.user.class1:
            # 获取同班同学的成绩并排序
            classmates_records = ExamRecord.objects.filter(
                exam_paper__number=exam_id,
                user__class1=record.user.class1
            )
            
            # 计算所有同班同学的总分
            classmates_with_scores = []
            for classmate_record in classmates_records:
                # 获取答题详情
                classmate_answer_details = AnswerDetail.objects.filter(record_id=classmate_record.number)
                
                # 计算同班同学的客观题和主观题得分
                classmate_objective_score = 0
                classmate_subjective_score = 0
                
                for answer_detail in classmate_answer_details:
                    # 根据 type1 字段判断题型
                    if answer_detail.type1 in OBJECTIVE_TYPES:  # 客观题
                        classmate_objective_score += answer_detail.score or 0
                    else:  # 主观题
                        classmate_subjective_score += answer_detail.score or 0
                
                # 计算同班同学的总分
                classmate_total_score = classmate_objective_score + classmate_subjective_score
                
                classmates_with_scores.append({
                    'record': classmate_record,
                    'total_score': classmate_total_score
                })
            
            # 按总分排序
            classmates_with_scores.sort(key=lambda x: x['total_score'], reverse=True)
            
            # 查找当前记录的排名
            for i, classmate_data in enumerate(classmates_with_scores):
                if classmate_data['record'].number == record.number:
                    class_rank = i + 1
                    break
        
        # 获取学生姓名
        student_name = "未知学生"
        if record.user and record.user.last_name and record.user.first_name:
            student_name = f"{record.user.last_name}{record.user.first_name}"
        elif record.user and record.user.first_name:
            student_name = record.user.first_name
        
        # 获取班级名称
        class_name = "未知班级"
        if record.user and hasattr(record.user, 'class1') and record.user.class1:
            try:
                # 更安全地访问班级名称
                class1_obj = record.user.class1
                # 尝试不同的方式获取班级名称
                if hasattr(class1_obj, 'class1') and class1_obj.class1 and hasattr(class1_obj.class1, 'class_name'):
                    class_name = class1_obj.class1.class_name
                elif hasattr(class1_obj, 'name'):
                    class_name = class1_obj.name
                else:
                    # 如果以上方式都不行，就使用对象的字符串表示
                    class_name = str(class1_obj)
            except Exception as e:
                # 如果出现任何异常，使用默认值
                logger.warning(f"获取班级名称时出错: {e}")
                class_name = "未知班级"
        
        # 根据报表类型准备不同的数据
        if report_type == 'analysis':
            # 成绩分析报告，添加更多分析数据
            report_data.append({
                '学号': record.user.id if record.user else '未知',
                '姓名': student_name,
                '班级': class_name,
                '客观题得分': objective_score,
                '主观题得分': subjective_score,
                '总分': total_score,
                '班级排名': class_rank,
                '客观题得分率': f"{(objective_score / (objective_score + subjective_score) * 100) if (objective_score + subjective_score) > 0 else 0:.2f}%",
                '主观题得分率': f"{(subjective_score / (objective_score + subjective_score) * 100) if (objective_score + subjective_score) > 0 else 0:.2f}%"
            })
        elif report_type == 'ranking':
            # 排名表，只包含排名相关信息
            report_data.append({
                '学号': record.user.id if record.user else '未知',
                '姓名': student_name,
                '班级': class_name,
                '总分': total_score,
                '班级排名': class_rank
            })
        else:  # 默认成绩单
            report_data.append({
                '学号': record.user.id if record.user else '未知',
                '姓名': student_name,
                '班级': class_name,
                '客观题得分': objective_score,
                '主观题得分': subjective_score,
                '总分': total_score,
                '班级排名': class_rank
            })
    
    # 如果是按分数排序，需要根据计算出的总分重新排序
    if sort_by == 'score':
        report_data.sort(key=lambda x: x['总分'], reverse=True)
    
    print(f"!!! REPORT DATA SIZE: {len(report_data)} !!!")
    logger.info(f"Report data size: {len(report_data)}")
    
    # 即使没有数据也返回空列表而不是404错误，支持预览功能
    if not report_data:
        return JsonResponse([], safe=False)
    
    # 检查是否是预览请求（通过XHR头或缺少format_type参数判断）
    is_preview = (
        request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' or 
        'format_type' not in request.GET
    )
    
    # 如果是预览请求，返回JSON格式数据
    if is_preview:
        return JsonResponse(report_data, safe=False)
    
    # 创建DataFrame
    df = pd.DataFrame(report_data)
    
    # 根据请求格式返回不同类型的文件
    format_type = params.get('format_type', 'xlsx')  # 改为format_type而不是format
    print(f"!!! FORMAT TYPE: {format_type}")
    
    # 确保所有字符串列都使用UTF-8编码
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str)
    
    if format_type == 'csv':
        print("!!! GENERATING CSV FILE !!!")
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = f'attachment; filename="{exam_name}_成绩报表.csv"'
        response.write('\ufeff')  # BOM for Excel
        df.to_csv(response, index=False, encoding='utf-8-sig')
        print("!!! CSV FILE GENERATED SUCCESSFULLY !!!")
        return response
    else:  # 默认返回xlsx
        print("!!! GENERATING XLSX FILE (DEFAULT) !!!")
        try:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # 确保中文字符正确编码
                df.to_excel(writer, sheet_name='成绩报表', index=False)
            output.seek(0)
            
            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{exam_name}_成绩报表.xlsx"'
            print("!!! XLSX FILE GENERATED SUCCESSFULLY !!!")
            return response
        except Exception as e:
            logger.error(f"生成Excel文件时出错: {e}")
            print(f"!!! ERROR GENERATING XLSX FILE: {e} !!!")
            # 如果xlsx生成失败，返回CSV格式
            response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
            response['Content-Disposition'] = f'attachment; filename="{exam_name}_成绩报表.csv"'
            response.write('\ufeff')  # BOM for Excel
            df.to_csv(response, index=False, encoding='utf-8-sig')
            print("!!! FALLBACK TO CSV FILE !!!")
            return response
