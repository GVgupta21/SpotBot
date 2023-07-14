// // const axios = require("axios");
// const helloWorldCard = require("./adaptiveCards/helloworldCommand.json");
// const { spawn } = require('child_process');
// // const {WaterfallDialog} = require('botbuilder-dialogs');
// const { AdaptiveCards } = require("@microsoft/adaptivecards-tools");
// const { CardFactory, MessageFactory } = require("botbuilder");
// const pyodide = require('pyodide');
// // var requestPromise = require('request-promise');

// class PrintDataHandler {
//   triggerPatterns = "B";

//   async handleCommandReceived(context, message) {
//     // verify the command arguments which are received from the client if needed.
//     console.log(`App received message: ${message.text}`);
//     // const username = "GVgupta";
//     // const password = "Gaurav@2101";
//     // const base64encodedData =(username + ':' + password);
//     // requestPromise.get({
//     //     uri: 'http://localhost:8080/job/PrintData/build?token=PrintData',
//     //     headers: {
//     //       'Authorization': 'Basic ' + base64encodedData
//     //     },
//     //     json: true
//     //   })
//     //   .then(function ok(jsonData) {
//     //     console.dir(jsonData);
//     //   })
//     //   .catch(function fail(error) {
//     //     console.log(error)
//     //     // handle error
//     //   });
//     // context.MessageFactory.text("Fetching Your Data....");
//     const pythonScript = spawn('/Library/Frameworks/Python.framework/Versions/3.11/bin/python3', ['/Users/gaurav.gupta2/Documents/program/progs/Print_Data.py']);

//     // Capture the output of the Python script
//     let link = "";
//     await new Promise((resolve, reject) => {
//       pythonScript.stdout.on('data', (data) => {
//         link = data.toString();
//         console.log(`Python script output: ${link}`);
//         resolve();
//       });

//       pythonScript.stderr.on('data', (data) => {
//         console.error(`Error executing Python script: ${data}`);
//         reject();
//       });

//       pythonScript.on('close', (code) => {
//         console.log(`Python script completed with code ${code}`);
//         resolve();
//       });
//     });
//     console.log("done");
//     return MessageFactory.text(`Link for Excel: ${link}`);
//   }
// }

// module.exports = {
//   PrintDataHandler,
// };
