function handlePinInputs(selector) {
    const inputs = document.querySelectorAll(selector);

    inputs.forEach((input, index) => {

        input.addEventListener("input", (e) => {
            e.target.value = e.target.value.replace(/[^0-9]/g, "");

            if (e.target.value.length === 1 && index < inputs.length - 1) {
                inputs[index + 1].focus();
            }
        });

        input.addEventListener("keydown", (e) => {
            if (e.key === "Backspace" && !input.value && index > 0) {
                inputs[index - 1].focus();
            }
        });

        input.addEventListener("paste", e => e.preventDefault());
    });
}