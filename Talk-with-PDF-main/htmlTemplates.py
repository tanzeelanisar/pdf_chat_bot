css = '''
<style>
body {
    background-color: #f5f5f5;
    font-family: 'Arial', sans-serif;
}

.chat-container {
    max-width: 800px;
    margin: auto;
}

.chat-message {
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    display: flex;
    align-items: flex-start;
    background-color: #fff;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.chat-message.user {
    justify-content: flex-end;
    align-items: flex-end;
}

.chat-message .avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    overflow: hidden;
    margin-right: 0.5rem;
}

.chat-message .avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.chat-message .message {
    flex: 1;
    padding: 0.5rem;
    background-color: #f0f0f0;
    border-radius: 4px;
    color: #333;
}

.chat-message.bot .message {
    background-color: #002147;
    color: #fff;
}

.user-input {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    margin-top: 1rem;
}

</style>

'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://i.ibb.co/cN0nmSj/Screenshot-2023-05-28-at-02-37-21.png" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://www.iconpacks.net/icons/free-icons-6/free-user-yellow-circle-icon-20550-thumb.png" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
    </div>    
    <div class="message">{{MSG}}</div>
</div>
'''
