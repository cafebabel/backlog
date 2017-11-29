/* Preloader fadeout when page is loaded */
window.onload = function() {
    const preloader = document.querySelector('#preloader');
    preloader.classList.add('fadeout');
    setTimeout(() => {
        preloader.classList.add('hidden')
    }, 300);
}

/* open menu */
const menuButton = document.querySelector('button.menu-button');
menuButton.addEventListener('click', () => {
    menuButton.classList.toggle('active')
})

/* external link in new tab */
Array.from(document.querySelectorAll('a')).forEach(a => {
    if (a.href.search(/\w+:\/\//) === 0 && a.hostname !== location.hostname) a.setAttribute('target', '_blank')
})

/* animation flash info */
const flashes = document.querySelector('.flashes');
if (flashes) {
    setTimeout(() => {
        flashes.classList.add('hidden')
    }, 3000)
}

/* display profile social network field on click */
const socialIcon = document.querySelector('.social-networks li');
socialIcon.addEventListener('click', (event) => {
    event.preventDefault();
    this.document.querySelector('label').classList.toggle('active')
});

/* animation login fields */
Array.from(document.querySelectorAll('form[name=login_user_form] input')).forEach(input => {
    const parent = input.parentElement
    input.addEventListener('focus', _ => {
    console.log('focus')
    parent.classList.add('active', 'completed')
    })
input.addEventListener('blur', _ => {
    if (input.value) return
parent.classList.remove('active', 'completed')
    })
})

