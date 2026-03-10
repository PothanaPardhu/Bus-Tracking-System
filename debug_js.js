const fs=require('fs');
let path='c:/Users/HP/Downloads/MIPL-PMJ-25037 QR SCAN BASED INTELLIGENT SYSTEM FOR SCHOOL BUS TRACKING/assets/template/user/user-tracking-realtime.html';
let text=fs.readFileSync(path,'utf8');
let script=text.split('<script>')[1].split('</script>')[0];
script=script.replace(/{{[^}]*}}/g,'0');
console.log('script length', script.length);
// print around location 306 (error offset) and maybe more
let idx=306;
console.log('around 306:', script.slice(idx-50, idx+50));

try{
    eval(script);
    console.log('parsed ok');
}catch(e){
    console.error('eval error', e.message);
    console.error(e.stack);
    // print last 100 chars
    console.log('last chars', script.slice(-200));
}
