;
// document.write('<script src="{% static " js/vue.js " %}"></script>')
Vue.config.delimiters = ["[[", "]]"];
Vue.component('my-button', {
    template: '\
                <a :href="my_href">\
                <div\
                    class="my-button"\
                    :id="id"\
                    :style="style_object"\
                    @mouseover="mouseover"\
                    @mouseout="mouseout"\
                >\
                    <slot></slot>\
                </div>\
                </a>\
            ',
    props: ['href', 'id', 'color'],
    data: function() {
        this.my_color = this.color ? this.color : 'rgb(105, 105, 105)'
        return {
            delay: 300,
            white: 'rgb(255, 255, 255)',
            my_href: this.href ? this.href : 'javascript:;',
            style_object: {
                color: this.my_color,
                borderColor: this.my_color,
                backgroundColor: 'rgb(255, 255, 255)'
            }
        }
    },
    methods: {
        mouseover: function() {
            console.log('in')
            this.style_object.color = this.white
            this.style_object.backgroundColor = this.my_color
        },
        mouseout: function() {
            console.log('out')
            this.style_object.color = this.my_color
            this.style_object.backgroundColor = this.white
        }
    }
});