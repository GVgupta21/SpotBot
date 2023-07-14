const { ActivityHandler, MessageFactory } = require('botbuilder');
const { DialogSet, WaterfallDialog, TextPrompt, ComponentDialog } = require('botbuilder-dialogs');
const { ConversationState, MemoryStorage } = require('botbuilder');

const convoState = new ConversationState(new MemoryStorage());
const dialogState = convoState.createProperty('dialogState');
const dialogs = new DialogSet(dialogState);

class AlertHandler extends ComponentDialog {
  constructor(dialogId) {
    super(dialogId);
    this.dialogSet = dialogs;
    this.convoState = convoState;

    const waterfallDialog = new WaterfallDialog('waterfallDialog', [
      async (step) => {
        // Step 1: Prompt the user for input
        const promptOptions = {
          prompt: 'Please enter your name.',
        };
        return await step.prompt('textPrompt', promptOptions);
      },
      async (step) => {
        // Step 2: Retrieve the user's name and display a message
        const name = step.result;
        await step.context.sendActivity(`Hello, ${name}!`);
        return await step.next();
      },
      async (step) => {
        // Step 3: Handle dialog end and display the dialog stack
        const dialogStack = step.context.stack;
        console.log(dialogStack);

        return await step.endDialog();
      },
    ]);

    this.dialogSet.add(waterfallDialog);

    // Add a text prompt to the dialog set
    this.dialogSet.add(new TextPrompt('textPrompt'));
  }

  async onBeginDialog(innerDc, options) {
    // Start the waterfall dialog when the component dialog is started
    return await innerDc.beginDialog('waterfallDialog');
  }
}

class MyBot extends ActivityHandler {
  constructor() {
    super();

    // Create an instance of the AlertHandler
    const alertHandler = new AlertHandler('alertHandler');

    // Register the alertHandler as the root dialog
    this.dialogs = new DialogSet(dialogState);
    this.dialogs.add(alertHandler);

    this.onMessage(async (context, next) => {
      const dc = await this.dialogs.createContext(context);
      await dc.beginDialog(alertHandler.id);

      await next();
    });
  }

  async run(context) {
    await super.run(context);

    // Save any changes to the conversation state
    await convoState.saveChanges(context);
  }
}

module.exports.MyBot = MyBot;
