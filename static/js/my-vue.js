;
Vue.component('my-button', {
    template: '\
                <a\
                    class="my-button"\
                    :href="href"\
                    :style="style_object"\
                    :id="id"\
                    @mouseover="mouseover"\
                    @mouseout="mouseout"\
                    @click="click"\
                >\
                    <slot>{{text}}</slot>\
                </a>\
            ',
    props: {
        id: String,
        text: String,
        href: {
            type: String,
            default: 'javascript:;'
        },
        color: {
            type: String,
            default: 'rgb(105, 105, 105)'
        },
        font: {
            type: [String, Number],
            default: 16
        },
        click: {
            type: [String, Function],
            default: ""
        }
    },
    data: function() {
        return {
            white: 'rgb(255, 255, 255)',
            style_object: {
                color: this.color,
                borderColor: this.color,
                fontSize: this.font,
                backgroundColor: 'rgb(255, 255, 255)',
                width: '5em',
                height: '2em',
                margin: '1em 0',
                display: 'inline-block',
                position: 'relative',
                padding: '0 1em',
                lineHeight: '2em',
                borderRadius: '1em',
                border: '1px solid',
                textDecoration: 'none'
            }
        }
    },
    methods: {
        mouseover: function() {
            this.style_object.color = this.white
            this.style_object.backgroundColor = this.color
        },
        mouseout: function() {
            this.style_object.color = this.color
            this.style_object.backgroundColor = this.white
        }
    },
    watch: {
        font: function (val, old_val) {
            this.style_object.fontSize = val
        },
        color: function (val, old_val) {
            this.style_object.borderColor = val
            this.style_object.color = val
            this.style_object.backgroundColor = this.white
        }
    }
})

function center(vm_style) {
    var left = (window.innerWidth - vm_style.width) / 2
    var top = (window.innerHeight - vm_style.height) / 2
    vm_style.left = left
    vm_style.top = top
}