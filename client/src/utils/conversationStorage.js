/**
 * Simple conversation storage for single conversation mode
 */

const STORAGE_KEY = 'current_conversation';

export const conversationStorage = {
  /**
   * Get the current conversation from localStorage
   * @returns {Object|null} Conversation object or null
   */
  getCurrentConversation: () => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : null;
    } catch (error) {
      console.error('Error loading conversation:', error);
      return null;
    }
  },

  /**
   * Save the current conversation to localStorage
   * @param {Object} conversation - Conversation object to save
   */
  saveCurrentConversation: (conversation) => {
    try {
      const updatedConversation = {
        ...conversation,
        updatedAt: new Date().toISOString()
      };
      
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedConversation));
      console.log('Conversation saved:', updatedConversation.id);
    } catch (error) {
      console.error('Error saving conversation:', error);
    }
  },

  /**
   * Add a message to the current conversation
   * @param {Object} message - The message object to add
   */
  addMessage: (message) => {
    const conversation = conversationStorage.getCurrentConversation();
    if (conversation) {
      if (!conversation.messages) {
        conversation.messages = [];
      }
      conversation.messages.push(message);
      conversationStorage.saveCurrentConversation(conversation);
    }
  },

  /**
   * Clear the current conversation
   */
  clearConversation: () => {
    localStorage.removeItem(STORAGE_KEY);
    console.log('Conversation cleared');
  }
};
