class FormValidator {

    constructor(formId, rules) {

        this.form = $(formId)
        this.rules = rules

        this.init()

    }

    init() {

        let self = this

        this.form.find(".form-control").on("input", function () {
            self.validateField($(this))
        })

        this.form.on("submit", function (e) {

            e.preventDefault()

            if (self.validateForm()) {
                self.form.trigger("validSubmit")
            }

        })

    }

    validateForm() {

        let valid = true

        for (let field in this.rules) {

            let input = this.form.find("[name=" + field + "]")

            if (!this.validateField(input)) {
                valid = false
            }

        }

        return valid

    }

    validateField(input) {

        let name = input.attr("name")
        let value = $.trim(input.val())
        let rule = this.rules[name]

        if (!rule) return true

        let error = ""

        if (rule.required && !value) {
            error = rule.required
        }

        if (!error && rule.regex && value && !rule.regex.test(value)) {
            error = rule.invalid
        }

        if (!error && rule.min && value.length < rule.min) {
            error = rule.minMsg
        }

        if (error) {

            input.addClass("input-error")
            $("." + name + "_error").text(error)

            return false

        }

        input.removeClass("input-error")
        $("." + name + "_error").text("")

        return true

    }

}