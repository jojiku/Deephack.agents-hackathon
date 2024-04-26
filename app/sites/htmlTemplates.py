css = '''
    <style>
    .chat-message {
        padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex; justify-content: space-between;
    }
    .chat-message.user {
        background-color: #b0b0b0;  /* Changed to grey */
    }
    .chat-message.bot {
        background-color: #475063;
    }
    .chat-message .avatar {
      width: 15%;  /* Reduced width */
    }
    .chat-message .avatar img {
      max-width: 58px;  /* Reduced size */
      max-height: 58px;
      border-radius: 50%;
      object-fit: cover;
    }
    .chat-message .message {
      width: 70%;  /* Reduced width */
      padding: 0 1rem;  /* Adjusted padding */
      color: #fff;
    }
    </style>
    '''

bot_template = '''
<div class="chat-message bot"> 
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="message">{{MSG}}</div>
</div>
'''