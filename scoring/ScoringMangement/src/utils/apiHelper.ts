import { markAsRead as markAsReadApi, type Notification } from '../api1/notificationApi'

/**
 * 标记通知为已读的辅助函数
 * 包含错误处理和重试机制
 * @param notificationId 通知ID
 * @returns Promise<Notification> 更新后的通知对象
 */
export const markNotificationAsRead = async (notificationId: number): Promise<Notification> => {
  try {
    // 首先尝试使用标准API
    const response = await markAsReadApi(notificationId)
    return response.data
  } catch (error) {
    console.warn(`标记通知 ${notificationId} 为已读失败，尝试备用方法:`, error)

    // 如果标准方法失败，抛出错误让调用者处理
    throw error
  }
}
