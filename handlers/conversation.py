from telegram.ext import  ConversationHandler, CallbackContext

class CustomConversationHandler(ConversationHandler):
    def _trigger_timeout(self, context, job=None):
        self.logger.debug('conversation timeout was triggered!')

        if isinstance(context, CallbackContext):
            context = context.job.context
        else:
            context = job.context
        print(context.__dict__)
        print(context.conversation_key)
        del self.timeout_jobs[context.conversation_key]
        handlers = self.states.get(self.TIMEOUT, [])
        for handler in handlers:
            check = handler.check_update(context.update)
            print('CHECK??! ', check)
            print('UPDATE???', context.update)
            if check is not None and check is not False:
                handler.handle_update(context.update, context.dispatcher, check)
        self.update_state(self.END, context.conversation_key)