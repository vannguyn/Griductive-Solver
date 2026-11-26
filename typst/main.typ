#import "template.typ": *

#show: fit_report.with(
  course_id: "CSC14003",
  course_name: "NHẬP MÔN TRÍ TUỆ NHÂN TẠO",
  report_subtitle: "BÁO CÁO ĐỒ ÁN MÔN HỌC",
  report_title: "GRIDUCTIVE SOLVER",
  instructor: "TS. Bùi Tiến Lên",
  class_id: "24_22",
  academic_year: "Học kỳ I, 2026 - 2027",
  students: (
    ("24120127", "Nguyễn Ngọc Quang", "24120127@student.hcmus.edu.vn"),
    ("24120134", "Lương Nhật Tân", "24120134@student.hcmus.edu.vn"),
    ("24120185", "Nguyễn Gia Hưng", "24120185@student.hcmus.edu.vn"),
    ("24120202", "Võ Nhật Minh", "24120202@student.hcmus.edu.vn"),
    ("24120205", "Trần Văn Nguyên", "24120205@student.hcmus.edu.vn"),
  ),
  is_project_report: true,
)

#include "sections/01_introduction.typ"
#include "sections/02_problem_formulation.typ"                        
#include "sections/03_architecture.typ"
#include "sections/04_algorithms.typ"
#include "sections/05_gui_and_gameplay.typ"
#include "sections/06_experiments.typ"
#include "sections/07_evaluation.typ"
#include "sections/08_appendix_ai.typ"

                                                                                                                                                                                                             