import { createRouter, createWebHistory } from 'vue-router'
import AutoGradeObjective from '@/views/grading/AutoGradeObjective.vue'
import ManualGradeSubjective from '@/views/grading/ManualGradeSubjective.vue'
import GradeSummary from '@/views/grading/GradeSummary.vue'
import StudentPersonalReport from '@/views/reports/StudentPersonalReport.vue'
import ExportGradeReport from '@/views/reports/ExportGradeReport.vue'
import LoginRegister from "@/views/login/LoginRegister.vue";
import MainPage from "@/views/login/MainPage.vue";
import PersonPage from "@/views/login/PersonPage.vue";
import ManageUser from "@/views/login/ManageUser.vue";
import review from "@/views/review.vue";
import vuew_question_bank_list from "@/views/views/vuew_question_bank_list.vue";
import Question_bank_list from "@/views/views/question_bank_list.vue";
import topic_list from "@/views/views/topic_list.vue";
import addtopic from "@/views/views/addtopic.vue";
import topic_modify from "@/views/views/topic_modify.vue";
import add_gap_topic from "@/views/views/add_gap_topic.vue";
import add_judge_topic from "@/views/views/add_judge_topic.vue";
import add_short_topic from "@/views/views/add_short_topic.vue";
import edit_gap_topic from "@/views/views/edit_gap_topic.vue";
import edit_judge_topic from "@/views/views/edit_judge_topic.vue";
import edit_short_topic from "@/views/views/edit_short_topic.vue";
import vuew_topic_list from "@/views/views/vuew_topic_list.vue";
import vuew_topic from "@/views/views/vuew_topic.vue";
import admin_question_list from "@/views/views/admin_question_list.vue";
import add_subject from "@/views/views/add_subject.vue";
import audit from "@/views/views/audit.vue";
import add_grade from "@/views/views/add_grade.vue"
import App1 from "@/views/views-wrong/App1.vue";
import WrongTopicsView from "@/views/views-wrong/WrongTopicsView.vue";
import ContactRecordsView from "@/views/views-wrong/ContactRecordsView.vue";
import ReviewRecordsView from "@/views/views-wrong/ReviewRecordsView.vue";
import AIAssistantView from "@/views/views-wrong/AIAssistantView.vue";
import NotificationView from "@/views/views-notice/NotificationView.vue";
import Appg from "@/views/views-notice/Appg.vue";
import HomeView from "@/views/viewshu/HomeView.vue";
import ExamManagementView from "@/views/viewshu/ExamManagementView.vue";
import TakeExamView from "@/views/viewshu/TakeExamView.vue";
import ExamPaperView from "@/views/viewshu/ExamPaperView.vue";

const routes = [
  {
    path: '/exam-management',
    name: 'ExamManagement',
    component: ExamManagementView
  },
  {
    path: '/take-exam',
    name: 'TakeExam',
    component: TakeExamView
  },
  // 添加 ExamPaper 路由
  {
    path: '/exam/:examPaperId',
    name: 'ExamPaper',
    component: ExamPaperView,
    props: true
  },
  {
      path: '/notification',
      name: 'notification',
      component: NotificationView,
    },
  {
  path: '/api11',
  component: () => import('@/views/views-wrong/App1.vue'),
  children: [
    {
      path: 'wrong-topics',
      name: 'WrongTopics',
      component: () => import('@/views/views-wrong/WrongTopicsView.vue')
    },
    {
      path: 'contact-records',
      name: 'ContactRecords',
      component: () => import('@/views/views-wrong/ContactRecordsView.vue')
    },
    {
      path: 'review-records',
      name: 'ReviewRecords',
      component: () => import('@/views/views-wrong/ReviewRecordsView.vue')
    },
    {
      path: 'ai',
      name: 'AIAssistant',
      component: () => import('@/views/views-wrong/AIAssistantView.vue')
    }
  ]
  },

  {path: '/', redirect: '/login'},
  {
    path: '/list',
    name: 'QuestionBankList',
    component: Question_bank_list
  },
  {
    path: '/topic/:id',
    name: 'topic_list',
    component: topic_list,
    props: true
  },
  {
    path: '/add_topic/:bankId/:type1',
    name: 'add_topic',
    component: addtopic,
    props: true
  },
  {
    path: '/topic_modify/:bankId/:id/:type',
    name: 'topic_modify',
    component: topic_modify,
    props: true
  },
  {
    path: '/add_gap_topic/:bankId',
    name: 'add_gap_topic',
    component: add_gap_topic,
    props: true
  },
  {
    path: '/add_judge_topic/:bankId',
    name: 'add_judge_topic',
    component: add_judge_topic,
    props: true
  },
  {
    path: '/add_short_topic/:bankId',
    name: 'add_short_topic',
    component: add_short_topic,
    props: true
  },
  {
    path: '/edit_gap_topic/:bankId/:id',
    name: 'edit_gap_topic',
    component: edit_gap_topic,
    props: true
  },
  {
    path: '/edit_judge_topic/:bankId/:id',
    name: 'edit_judge_topic',
    component: edit_judge_topic,
    props: true
  },
  {
    path: '/edit_short_topic/:bankId/:id',
    name: 'edit_short_topic',
    component: edit_short_topic,
    props: true
  },
  {
    path: '/view_question',
    name: 'view_question',
    component: vuew_question_bank_list,
    props: true
  },
  {
    path: '/view_topic/:id',
    name: 'view_topic',
    component: vuew_topic_list,
    props: true
  },
  {
    path: '/vuew_topic',
    name: 'vuew_topic',
    component: vuew_topic,
    props: true

  },
  {
    path: '/admin_question',
    name: 'admin_question',
    component: admin_question_list,
    props: true
  },
   {
    path: '/add_subject',
    name: 'add_subject',
    component: add_subject,
    props: true
  },
  {
    path: '/add_grade',
    name: 'add_grade',
    component: add_grade,
    props: true
  },
  {
    path: '/audit',
    name: 'audit',
    component: audit,
    props: true
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginRegister
  },
  {
    path: '/auto-grade',
    name: 'AutoGradeObjective',
    component: AutoGradeObjective,
    meta: { requiresTeacher: true }
  },
  {
    path: '/manual-grade',
    name: 'ManualGradeSubjective',
    component: ManualGradeSubjective,
    meta: { requiresTeacher: true }
  },
  {
    path: '/grade-summary',
    name: 'GradeSummary',
    component: GradeSummary,
    meta: { requiresTeacher: true }
  },
  {
    path: '/student-report',
    name: 'StudentPersonalReport',
    component: StudentPersonalReport
  },
  {
    path: '/export-report',
    name: 'ExportGradeReport',
    component: ExportGradeReport,
    meta: { requiresTeacher: true }
  },
  {
    path: '/main',
    name: 'MainPage',
    component: MainPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/person',
    name: 'PersonPage',
    component: PersonPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/manageuser',
    name: 'ManageUser',
    component: ManageUser,
    meta: { requiresAuth: true }
  },
  {
    path: '/error-book',
    name: 'error-book',
    component: App1,
    meta: { requiresAuth: true }
  },
  {
    path: '/review',
    name: 'Review',
    component: review,
    meta: { requiresAuth: true },
    redirect: { name: 'AutoGradeObjectiveChild' },
    children: [
      {
        path: 'auto-grade',
        name: 'AutoGradeObjectiveChild',
        component: AutoGradeObjective,
        meta: { requiresTeacher: true }
      },
      {
        path: 'manual-grade',
        name: 'ManualGradeSubjectiveChild',
        component: ManualGradeSubjective,
        meta: { requiresTeacher: true }
      },
      {
        path: 'grade-summary',
        name: 'GradeSummaryChild',
        component: GradeSummary,
        meta: { requiresTeacher: true }
      },
      {
        path: 'export-report',
        name: 'ExportGradeReportChild',
        component: ExportGradeReport,
        meta: { requiresTeacher: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 添加导航守卫
router.beforeEach((to, from, next) => {
    // 检查目标路由是否需要登录
    if (to.matched.some(record => record.meta.requiresAuth)) {
        // 如果用户未登录，重定向到登录页面
        if (localStorage.getItem('access_token') === null) {
            next({ path: '/login' })
        } else {
            next() // 如果用户已登录，允许导航
        }
    } else {
        next() // 如果目标路由不需要登录，允许导航
    }
})


export default router
