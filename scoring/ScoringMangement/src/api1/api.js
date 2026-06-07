import { wrongTopicsApi } from './wrongTopics.js'
import { contactRecordsApi } from './contactRecords.js'
import { reviewRecordsApi } from './reviewRecords.js'
import { aiApi } from './ai.js'

const apiService = {
  wrongTopics: wrongTopicsApi,
  contactRecords: contactRecordsApi,
  reviewRecords: reviewRecordsApi,
  ai: aiApi
}

export default apiService
