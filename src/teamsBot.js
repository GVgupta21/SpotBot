const { TeamsActivityHandler, MessageFactory, CardFactory } = require("botbuilder");
const { DialogSet, WaterfallDialog, TextPrompt, ChoicePrompt } = require('botbuilder-dialogs');
const { ConversationState, MemoryStorage } = require('botbuilder');
const { AdaptiveCards } = require("@microsoft/adaptivecards-tools");
const { spawn } = require('child_process');
const convoState = new ConversationState(new MemoryStorage());
const dialogs = new DialogSet(convoState.createProperty('dialogState'));
const AWSCommandCard = require('./adaptiveCards/AWSCommand.json');
const AzureCommandCard = require('./adaptiveCards/AzureCommand.json');
const AWSAlert = require('./adaptiveCards/AWSAlert.json');
const AzureAlert = require('./adaptiveCards/AzureAlert.json');
const { ChoiceOutputFormat } = require("botbuilder-dialogs-adaptive");
// const { IncomingMessage } = require("http");

class AlertHandler extends WaterfallDialog {
  constructor() {
    let choice;
    const cloudProvider = 'AWS';
    super('waterfallDialog');

    const validLocations = ['ap-northeast-1a','ap-northeast-1c','ap-northeast-1d','ap-northeast-2a','ap-northeast-2b','ap-northeast-2c','ap-northeast-2d','ap-northeast-3a','ap-northeast-3b','ap-northeast-3c','ap-south-1a','ap-south-1b','ap-south-1c','ap-southeast-1a','ap-southeast-1b','ap-southeast-1c','ap-southeast-2a','ap-southeast-2b','ap-southeast-2c','ca-central-1a','ca-central-1b','ca-central-1d','eu-central-1a','eu-central-1b','eu-central-1c','eu-north-1a','eu-north-1b','eu-north-1c','eu-west-1a','eu-west-1b','eu-west-1c','eu-west-2a','eu-west-2b','eu-west-2c','eu-west-3a','eu-west-3b','eu-west-3c','sa-east-1a','sa-east-1b','sa-east-1c','us-east-1a','us-east-1b','us-east-1c','us-east-1d','us-east-1e','us-east-1f','us-east-2a','us-east-2b','us-east-2c','us-west-1a','us-west-1c','us-west-2a','us-west-2b','us-west-2c','us-west-2d'];

    this.addStep(async (step) => {
      // Step 0: Ask for user's desired action
      return await step.prompt('choicePrompt', 'What would you like to do?', ['Set Alert', 'Obtain Data','Get Best Instance','Exit']);
    });

    this.addStep(async (step) => {
      // Step 1: Handle user's desired action
      choice = step.result.value;
      if (choice === 'Set Alert') {
        const card = CardFactory.adaptiveCard(JSON.parse(JSON.stringify(AWSAlert)));
        const message = MessageFactory.attachment(card);
        await step.context.sendActivity(message);
      } else if (choice === 'Obtain Data') {
        // Handle "Obtain Data" action here
        const pythonScript = spawn('/Library/Frameworks/Python.framework/Versions/3.11/bin/python3', ['/Users/gaurav.gupta2/Documents/program/progs/Print_Data.py']);
        // Capture the output of the Python script
        await step.context.sendActivity(MessageFactory.text("Fetching Your Data......"));
        let link = "";
        await new Promise((resolve, reject) => {
          pythonScript.stdout.on('data', (data) => {
            link = data.toString();
            console.log(`Python script output: ${link}`);
            resolve();
          });

          pythonScript.stderr.on('data', (data) => {
            console.error(`Error executing Python script: ${data}`);
            reject();
          });

          pythonScript.on('close', (code) => {
            console.log(`Python script completed with code ${code}`);
            resolve();
          });
        });
        console.log("done");
        await step.context.sendActivity(`Link for Excel: ${link}`);
        await step.context.sendActivity( `Anything else that I can do for you?`);
        return await step.replaceDialog('waterfallDialog');
      } else if (choice=='Get Best Instance') {
        const card = CardFactory.adaptiveCard(JSON.parse(JSON.stringify(AWSCommandCard)));
        const message = MessageFactory.attachment(card);
        await step.context.sendActivity(message);

        // Wait for user input and store the values from the card
         
        // ... Store other required values from the card

        // Proceed to the next step or execute the Python script with the stored values
        return await step.context.sendActivity("Enter Your Specifications for the instance.");
      }
      else 
      {
        await step.context.sendActivity(`Exited from AWS Services!.`);
        return await step.endDialog();
      }
    });

    this.addStep(async (step) => {
      // Step 2: Store and parse the user's input
      if(choice==='Set Alert')
      { 
        const userInput = await step.context.activity.value;
        step.values.minCPU = userInput.minCPU?userInput.minCPU:0;
        step.values.minMemory = userInput.minMemory?userInput.minMemory:0;
        step.values.ratio = userInput.ratio;
        step.values.location = userInput.location;
        step.values.price = userInput.price;

        const userId = step.context.activity.from.id;
        const teamName = step.context.activity.channelData.team.name;
        
        console.log("Step 1 completed");
        console.log(userId);
        console.log(teamName);
        const pythonScriptPath1 = '/Users/gaurav.gupta2/Documents/program/progs/CompareAWS.py';
        // Input data for the Python script 
        const inputData1 = [cloudProvider,step.values.ratio, step.values.location, step.values.price,step.values.minCPU ,step.values.minMemory];
        // Spawn a new Python process
        const pythonProcess1 = spawn('/Library/Frameworks/Python.framework/Versions/3.11/bin/python3', [pythonScriptPath1]);
        inputData1.forEach((input) => {
          pythonProcess1.stdin.write(input + '\n');
        });
        pythonProcess1.stdin.end();

        // Listen for output from the Python script
        let link= "";
        await new Promise((resolve, reject) => {
          pythonProcess1.stdout.on('data', (data) => {
            link = JSON.parse(data.toString());
            console.log(`Python script output`);
            resolve();
          });

          pythonProcess1.stderr.on('data', (data) => {
            console.error(`Error executing Python script: ${data}`);
            reject();
          });

          pythonProcess1.on('close', (code) => {
            console.log(`Python script completed with code ${code}`);
            resolve();
          });
        });
        
        if(Object.keys(link).length != 0)
        {
          await step.context.sendActivity(MessageFactory.text(`
           Alert! Spot Instance Price Drop \n\n`+
          `The prices of the following spot instances have been dropped: ${link}`));
          for (const category in link) {
            // console.log("Category:", category);
            await step.context.sendActivity(MessageFactory.text(`Category: ${category}`));
            for(const chip in link[category]){
              await step.context.sendActivity(MessageFactory.text(`Chip: ${chip}`));
              for(const ssd in link[category][chip]){
                await step.context.sendActivity(MessageFactory.text(`${ssd}`));
                for (const size in link[category][chip][ssd])
                {
                  await step.context.sendActivity(MessageFactory.text(`Instance: ${link[category][chip][ssd][size]["Instance"]} with Price: ${link[category][chip][ssd][size]["Price"]} and Size: ${size}`));
                }
              }
            }
            // console.log("******************************");
            // if(link[category].length==2)
            // await step.context.sendActivity(MessageFactory.text(`Instance: ${link[category][0].InstanceType}  \t\t`  +  '     ' + ` Price : ${link[category][0]["Price (Per Month)"]}\n\n`+
            // `Instance: ${link[category][1].InstanceType}  \t\t`  +  ` Price : ${link[category][1]["Price (Per Month)"]}\n\n`));
            // if(link[category].length==1)
            // await step.context.sendActivity(MessageFactory.text(`Instance: ${link[category][0].InstanceType}  \t\t`  +  ` Price : ${link[category][0]["Price (Per Month)"]}\n\n`));
        }
        }
        else
        {
          const pythonScriptPath = '/Users/gaurav.gupta2/Documents/program/progs/InputData.py';
        // Input data for the Python script 
        const inputData = [step.values.ratio, step.values.location, step.values.price, userId, teamName,cloudProvider ,step.values.minCPU ,step.values.minMemory];
        // Spawn a new Python process
        const pythonProcess = spawn('/Library/Frameworks/Python.framework/Versions/3.11/bin/python3', [pythonScriptPath]);
        inputData.forEach((input) => {
          pythonProcess.stdin.write(input + '\n');
        });
        pythonProcess.stdin.end();

        // Listen for output from the Python script
        let id = "";
        pythonProcess.stdout.on('data', (data) => {
          const output = data.toString();
          id = output;
          console.log('Python script output:', output);
        });

        // Listen for any errors that occur during execution
        pythonProcess.on('error', (error) => {
          console.error('An error occurred:', error.message);
        });

        // Listen for when the Python script finishes executing
        pythonProcess.on('close', (code) => {
          console.log('Python script execution completed with code:', code);
        });

        await step.context.sendActivity(MessageFactory.text("Your Alert Has been set, You Will get Notified When the price will Drop Below Set price Limit"));
      }
      }
      else if (choice==="Get Best Instance")
      {
        const userInput = await step.context.activity.value;
        step.values.ratio = userInput.ratio;
        step.values.location = userInput.location;
        step.values.exactCPU = userInput.exactCPU?userInput.exactCPU:-1;
        step.values.minCPU = userInput.minCPU?userInput.minCPU:0;
        step.values.minMemory = userInput.minMemory?userInput.minMemory:0;
        // cloudProvider = "AWS";
        console.log(step.values.ratio);
        const pythonScriptPath = '/Users/gaurav.gupta2/Documents/program/progs/First_Try.py';
        // Input data for the Python script 
        const inputData = [step.values.ratio, step.values.location, step.values.exactCPU, step.values.minCPU, step.values.minMemory,cloudProvider];
        // Spawn a new Python process
        const pythonProcess = spawn('/Library/Frameworks/Python.framework/Versions/3.11/bin/python3', [pythonScriptPath]);
        inputData.forEach((input) => {
          pythonProcess.stdin.write(input + '\n');
        });
        pythonProcess.stdin.end();

        // Listen for output from the Python script
        let link="";
        await new Promise((resolve, reject) => {
          pythonProcess.stdout.on('data', (data) => {
            link = JSON.parse(data.toString());
            console.log(`Python script output ${data}`);
            resolve();
          });

          pythonProcess.stderr.on('data', (data) => {
            console.error(`Error executing Python script: ${data}`);
            reject();
          });

          pythonProcess.on('close', (code) => {
            console.log(`Python script completed with code ${code}`);
            resolve();
          });
        });
        if(Object.keys(link).length === 0)
        {
          await step.context.sendActivity(`No instances found with the given specifictaions!`);
        }
        else
        {
          await step.context.sendActivity(MessageFactory.text(`Prices are in USD per Month`));
          for (const category in link) {
          // console.log("Category:", category);
          await step.context.sendActivity(MessageFactory.text(`Category: ${category}`));
          for(const chip in link[category]){
            await step.context.sendActivity(MessageFactory.text(`Chip: ${chip}`));
            for(const ssd in link[category][chip]){
              await step.context.sendActivity(MessageFactory.text(`${ssd}`));
              for (const size in link[category][chip][ssd])
              {
                await step.context.sendActivity(MessageFactory.text(`Instance: ${link[category][chip][ssd][size]["Instance"]} with Price: ${link[category][chip][ssd][size]["Price"]} and Size: ${size}`));
              }
            }
          }

          // console.log("******************************");
          // if(link[category].length==2)
          // await step.context.sendActivity(MessageFactory.text(`Instance: ${link[category][0].InstanceType}  \t\t`  +  '     ' + ` Price : ${link[category][0]["Price (Per Month)"]}\n\n`+
          // `Instance: ${link[category][1].InstanceType}  \t\t`  +  ` Price : ${link[category][1]["Price (Per Month)"]}\n\n`));
          // if(link[category].length==1)
          // await step.context.sendActivity(MessageFactory.text(`Instance: ${link[category][0].InstanceType}  \t\t`  +  ` Price : ${link[category][0]["Price (Per Month)"]}\n\n`));
      }}
      }
      await step.context.sendActivity( `Anything else that I can do for you?`);
      return await step.replaceDialog('waterfallDialog');
    });

    dialogs.add(this);
    dialogs.add(new TextPrompt('textPrompt'));
    dialogs.add(new ChoicePrompt('choicePrompt'));
  }
}

class AlertHandlerAzure extends WaterfallDialog {
  constructor() {
    super('waterfallDialog1');
    let choice;
    const validLocations = ['eastus', 'eastus2', 'westus', 'centralus', 'northcentralus', 'southcentralus', 'northeurope', 'westeurope', 'eastasia', 'southeastasia', 'japaneast', 'japanwest', 'australiaeast', 'australiasoutheast', 'australiacentral', 'brazilsouth', 'southindia', 'centralindia', 'westindia', 'canadacentral', 'canadaeast', 'westus2', 'westcentralus', 'uksouth', 'ukwest', 'koreacentral', 'koreasouth', 'francecentral', 'southafricanorth', 'uaenorth', 'switzerlandnorth', 'germanywestcentral', 'norwayeast', 'jioindiawest', 'westus3', 'swedencentral', 'qatarcentral', 'polandcentral'];

    this.addStep(async (step) => {
      // Step 0: Ask for user's desired action
      return await step.prompt('choicePrompt', 'What would you like to do in Azure?', ['Set Alert', 'Obtain Data','Get Best Instance','Exit']);
    });

    this.addStep(async (step) => {
      // Step 1: Handle user's desired action
      choice = step.result.value;

      if (choice === 'Set Alert') {
        const card = CardFactory.adaptiveCard(JSON.parse(JSON.stringify(AzureAlert)));
        const message = MessageFactory.attachment(card);
        await step.context.sendActivity(message);
      } else if (choice === 'Obtain Data') {
        // Handle "Obtain Data" action here
        const pythonScript = spawn('/Library/Frameworks/Python.framework/Versions/3.11/bin/python3', ['/Users/gaurav.gupta2/Documents/program/progs/Print_Data_Azure.py']);
        // Capture the output of the Python script
        await step.context.sendActivity(MessageFactory.text("Fetching Your Data......"));
        let link = "";
        await new Promise((resolve, reject) => {
          pythonScript.stdout.on('data', (data) => {
            link = data.toString();
            console.log(`Python script output: ${link}`);
            resolve();
          });

          pythonScript.stderr.on('data', (data) => {
            console.error(`Error executing Python script: ${data}`);
            reject();
          });

          pythonScript.on('close', (code) => {
            console.log(`Python script completed with code ${code}`);
            resolve();
          });
        });
        console.log("done");
        await step.context.sendActivity(`Link for Excel: ${link}`);
        await step.context.sendActivity( `Anything else that I can do for you?`);
        return await step.replaceDialog('waterfallDialog1');
      }
      else if (choice==="Get Best Instance")
      {
        const card = CardFactory.adaptiveCard(JSON.parse(JSON.stringify(AzureCommandCard)));
        const message = MessageFactory.attachment(card);
        await step.context.sendActivity(message);

        // Wait for user input and store the values from the card
         
        // ... Store other required values from the card

        // Proceed to the next step or execute the Python script with the stored values
        return await step.context.sendActivity("Enter Your Specifications for the instance.");
        
      }
      else 
      {
        await step.context.sendActivity(`Exited from Azure Services!.`);
        return await step.endDialog();
      }
    });

    this.addStep(async (step) => {
      // Step 2: Store and parse the user's input
      if(choice=="Set Alert")
        {
          const userInput = await step.context.activity.value;
        step.values.minCPU = userInput.minCPU?userInput.minCPU:0;
        step.values.minMemory = userInput.minMemory?userInput.minMemory:0;
        step.values.ratio = userInput.ratio;
        step.values.location = userInput.location;
        step.values.price = userInput.price;

        if (!validLocations.includes(step.values.location)) {
          await step.context.sendActivity(MessageFactory.text('Invalid location entered. Please enter a valid location.'));
          return await step.replaceDialog(this.id);
        }
        console.log(step.context);
        const userId = step.context.activity.from.id;
        const teamName = step.context.activity.channelData.teamsTeamId;
        const cloudProvider= 'Azure';
        console.log("Step 1 completed");
        console.log(userId);
        console.log(teamName);
        const pythonScriptPath1 = '/Users/gaurav.gupta2/Documents/program/progs/Compare.py';
          // Input data for the Python script 
          const inputData1 = [cloudProvider,step.values.ratio, step.values.location, step.values.price];
          // Spawn a new Python process
          const pythonProcess1 = spawn('/Library/Frameworks/Python.framework/Versions/3.11/bin/python3', [pythonScriptPath1]);
          inputData1.forEach((input) => {
            pythonProcess1.stdin.write(input + '\n');
          });
          pythonProcess1.stdin.end();

          // Listen for output from the Python script
          let link;
          await new Promise((resolve, reject) => {
            pythonProcess1.stdout.on('data', (data) => {
              link = JSON.parse(data.toString());
              console.log(`Python script output`);
              resolve();
            });

            pythonProcess1.stderr.on('data', (data) => {
              console.error(`Error executing Python script: ${data}`);
              reject();
            });

            pythonProcess1.on('close', (code) => {
              console.log(`Python script completed with code ${code}`);
              resolve();
            });
          });
          if(Object.keys(link).length != 0)
          {
            await step.context.sendActivity(MessageFactory.text(`
            Alert! Spot Instance Price Drop \n\n`+
            `Exciting news! The prices of the following spot instances have been dropped:\n\n`+
            `Prices are in USD per month`));
          }
          for (const inst in link)
          {
            await step.context.sendActivity(MessageFactory.text(`Category: ${category}`));
            if(link[category].length==3)
            await step.context.sendActivity(MessageFactory.text(`Instance: ${link[category][0].InstanceType}  \t\t`  +  ` Price : ${link[category][0]["Price (Per Month)"]}\n\n`+
            `Instance: ${link[category][1].InstanceType}  \t\t`  +  ` Price : ${link[category][1]["Price (Per Month)"]}\n\n`+
            `Instance: ${link[category][2].InstanceType}  \t\t`  +  ` Price : ${link[category][2]["Price (Per Month)"]}\n\n`));
            if(link[category].length==2)
            await step.context.sendActivity(MessageFactory.text(`Instance: ${link[category][0].InstanceType}  \t\t`  +  '     ' + ` Price : ${link[category][0]["Price (Per Month)"]}\n\n`+
            `Instance: ${link[category][1].InstanceType}  \t\t`  +  ` Price : ${link[category][1]["Price (Per Month)"]}\n\n`));
            if(link[category].length==1)
            await step.context.sendActivity(MessageFactory.text(`Instance: ${link[category][0].InstanceType}  \t\t`  +  ` Price : ${link[category][0]["Price (Per Month)"]}\n\n`));
          }
          if(Object.keys(link).length === 0)
        {
          const pythonScriptPath = '/Users/gaurav.gupta2/Documents/program/progs/InputData.py';
          // Input data for the Python script 
          const inputData = [step.values.ratio, step.values.location, step.values.price, userId, teamName,cloudProvider];
          // Spawn a new Python process
          const pythonProcess = spawn('/Library/Frameworks/Python.framework/Versions/3.11/bin/python3', [pythonScriptPath]);
          inputData.forEach((input) => {
            pythonProcess.stdin.write(input + '\n');
          });
          pythonProcess.stdin.end();

          // Listen for output from the Python script
          let id = "";
          pythonProcess.stdout.on('data', (data) => {
            const output = data.toString();
            id = output;
            console.log('Python script output:', output);
          });

          // Listen for any errors that occur during execution
          pythonProcess.on('error', (error) => {
            console.error('An error occurred:', error.message);
          });

          // Listen for when the Python script finishes executing
          pythonProcess.on('close', (code) => {
            console.log('Python script execution completed with code:', code);
          });

          await step.context.sendActivity(MessageFactory.text("Your Alert Has been set, You Will get Notified When the price will Drop Below Set price Limit"));
      }
    }
    else if(choice==="Get Best Instance")
    {
      const userInput = await step.context.activity.value;
        step.values.ratio = userInput.ratio;
        step.values.location = userInput.location;
        step.values.exactCPU = userInput.exactCPU?userInput.exactCPU:-1;
        step.values.minCPU = userInput.minCPU?userInput.minCPU:0;
        step.values.minMemory = userInput.minMemory?userInput.minMemory:0;
        let cloudProvider = "Azure";
        const pythonScriptPath = '/Users/gaurav.gupta2/Documents/program/progs/BestInstance.py';
        // Input data for the Python script 
        const inputData = [step.values.ratio, step.values.location,step.values.exactCPU ,step.values.minCPU, step.values.minMemory,cloudProvider];
        // Spawn a new Python process
        const pythonProcess = spawn('/Library/Frameworks/Python.framework/Versions/3.11/bin/python3', [pythonScriptPath]);
        inputData.forEach((input) => {
          pythonProcess.stdin.write(input + '\n');
        });
        pythonProcess.stdin.end();

        // Listen for output from the Python script
        let link;
        await new Promise((resolve, reject) => {
          pythonProcess.stdout.on('data', (data) => {
            link = JSON.parse(data.toString());
            console.log(`Python script output`);
            resolve();
          });

          pythonProcess.stderr.on('data', (data) => {
            console.error(`Error executing Python script: ${data}`);
            reject();
          });

          pythonProcess.on('close', (code) => {
            console.log(`Python script completed with code ${code}`);
            resolve();
          });
        });
        if(Object.keys(link).length === 0)
        {
          await step.context.sendActivity(`No instances found with the given specifictaions!`);
        }
        else
        {
          await step.context.sendActivity(MessageFactory.text(`Prices are in USD per month`));
          for (const category in link) {
          // console.log("Category:", category);
          await step.context.sendActivity(MessageFactory.text(`Category: ${category}`));
          if(link[category].length==3)
          await step.context.sendActivity(MessageFactory.text(`Instance: ${link[category][0].InstanceType}  \t\t`  +  ` Price : ${link[category][0]["Price (Per Month)"]}\n\n`+
          `Instance: ${link[category][1].InstanceType}  \t\t`  +  ` Price : ${link[category][1]["Price (Per Month)"]}\n\n`+
          `Instance: ${link[category][2].InstanceType}  \t\t`  +  ` Price : ${link[category][2]["Price (Per Month)"]}\n\n`));
          if(link[category].length==2)
          await step.context.sendActivity(MessageFactory.text(`Instance: ${link[category][0].InstanceType}  \t\t`  +  '     ' + ` Price : ${link[category][0]["Price (Per Month)"]}\n\n`+
          `Instance: ${link[category][1].InstanceType}  \t\t`  +  ` Price : ${link[category][1]["Price (Per Month)"]}\n\n`));
          if(link[category].length==1)
          await step.context.sendActivity(MessageFactory.text(`Instance: ${link[category][0].InstanceType}  \t\t`  +  ` Price : ${link[category][0]["Price (Per Month)"]}\n\n`));
      }}
    }
    await step.context.sendActivity( `Anything else that I can do for you?`);
      return await step.replaceDialog('waterfallDialog1');
    });

    dialogs.add(this);
    dialogs.add(new TextPrompt('textPrompt'));
    dialogs.add(new ChoicePrompt('choicePrompt'));
  }
}
class IncomingMessages extends WaterfallDialog{
  constructor() {
    super('waterfallDialog2');
    const alertHandler = new AlertHandler();
    const alertHandlerAzure = new AlertHandlerAzure();
    dialogs.add(new TextPrompt('textPrompt'));
    dialogs.add(new ChoicePrompt('choicePrompt'));
    this.addStep(async(step)=>{
      return await step.prompt('choicePrompt', "How can I assist you today? \n\n"+ 
      "Select one of the Cloud Providers to get information about corresponding", ['AWS instances', 'Azure instances','Exit']);
    });
    this.addStep(async(step)=>{
      let choice=step.result.value;
      const dc = await dialogs.createContext(step.context);
      if (choice ==="AWS instances")
      {
        return await dc.beginDialog(alertHandler.id);
      }
      else if(choice ==="Azure instances")
      {
        return await dc.beginDialog(alertHandlerAzure.id);
      }
      else if(choice==="Exit")
      {
        await step.context.sendActivity(`Thanks for using SpotBot!`);
        return await step.endDialog();
      }
      else{
        return await step.replaceDialog(this.id);
      }
    });
    this.addStep(async(step)=>{
      return step.replaceDialog('waterfallDialog2');
    });
    dialogs.add(this);
    
  }
}
class TeamsBot extends TeamsActivityHandler {
  constructor() {
    super();

    // Create an instance of the AlertHandler
    const incomingMessage = new IncomingMessages();
    const alertHandler = new AlertHandler();
    const alertHandlerAzure = new AlertHandlerAzure();
    dialogs.add(new ChoicePrompt('choicePrompt'));
    // this.dialogs = dialogs;
    this.onMessage(async (context, next) => {
      // Create a dialog context
      console.log(context.activity.channelData.channel);
      const dc = await dialogs.createContext(context);

      // Check if there's an active dialog in the dialog context
      if (dc.activeDialog) {
        // Continue the active dialog
        await dc.continueDialog();
      } else {
        // Check if the user's input matches the trigger pattern
        const text = context.activity.text;
        if (text.toLowerCase() === 'aws') {
          // Begin the waterfall dialog
          await dc.beginDialog(alertHandler.id);
        } 
        else if (text.toLowerCase() === 'azure'){
          await dc.beginDialog(alertHandlerAzure.id);
        }
        else {
          // Handle other user inputs here
          // await context.sendActivity(
          //   "How can I assist you today?\n\n" +
          //   "A. For Getting info about AWS Spot Instances \n\n" +
          //   "B. For Getting Info about Azure Spot Instances.\n\n" +
          //   "Please reply with the corresponding alphabet for the action you want to perform."
          // );
          await dc.beginDialog(incomingMessage.id);
          // return await context.prompt('choicePrompt', 'How can I assist you today?', ['Option 1', 'Option 2', 'Option 3']);
        }
      }

      // Save changes to the conversation state
      await convoState.saveChanges(context);

      // Continue with the remaining middleware pipeline
      await next();
    });
  }

  async run(context) {
    await super.run(context);
  }
}

module.exports.TeamsBot = TeamsBot;
