let golfFooter = document.getElementById('footer');
let jsonContainer = document.createElement("div");

jsonContainer.setAttribute('id', 'scrapy-scrapper');

golfFooter.appendChild(jsonContainer);

v = [];

((() => {
    const origOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function() {
        this.addEventListener('load', function() {
            console.log('request completed!');
            console.log(this.readyState); //will always be 4 (ajax is completed successfully)
            console.log(this.responseURL);
            v = [...v, ...JSON.parse(this.responseText)]
            jsonContainer.innerText = JSON.stringify(v);
            // console.log(jsonContainer.innerText);
        });
        origOpen.apply(this, arguments);
    };
}))();