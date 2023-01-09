// import Typewriter from 'typewriter-effect/dist/core';
// console.log(new Typewritter());

// var app = document.getElementById('app');
// var typewriter = new Typewriter(app, {
//     autoStart: true,
// });
// typewriter
//     .changeDelay(10)
//     .typeString('Hello c\'anat')
//     .pauseFor(300)
//     .typeString('What\'s up')
//     .pauseFor(500)
//     .deleteChars(8)
//     .typeString('EHEH')
//     .start

var app = document.getElementById('app');
var typewriter = new Typewriter(app, {
    autoStart: true,
    delay: 75,

});
typewriter
    .typeString('Pour me conytacter')
    .pauseFor(300)
    .deleteChars(7)
    .typeString('tacter,')
    .pauseFor(200)
    .typeString('voici mon mail :')
    .typeString('<br/>')
    .pauseFor(300)
    .typeString('<span style="color: #f54afb;">garnieranatole@gmail.com</span>')
    .start();