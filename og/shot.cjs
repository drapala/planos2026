const {chromium}=require('/Users/drapala/keranos/node_modules/playwright');
(async()=>{const b=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
const p=await b.newPage({viewport:{width:1200,height:630},deviceScaleFactor:1});await p.goto('file://'+require('path').join(__dirname,'card.html'));
await p.screenshot({path:''+require('path').join(__dirname,'..','site','og.png')+''});await b.close();})();
