let selectedPlan = null;

/* ✅ DOM READY */
document.addEventListener("DOMContentLoaded", function () {

    const amountInput = document.getElementById("rechargeAmount");
    const payBtn = document.getElementById("payBtn");

    /* ================= CARD CLICK ================= */
    document.querySelectorAll(".membership-card").forEach(card => {
        card.addEventListener("click", function () {

            // same card → deselect
            if (selectedPlan === this) {
                this.classList.remove("active");
                selectedPlan = null;
                amountInput.value = "";
                hidePreview();
                disablePay();
                return;
            }

            document.querySelectorAll(".membership-card")
                .forEach(c => c.classList.remove("active"));

            this.classList.add("active");
            selectedPlan = this;

            let amount = parseInt(this.dataset.amount);
            amountInput.value = amount;

            updatePreviewByAmount(amount);
        });
    });

    /* ================= INPUT CHANGE ================= */
    amountInput.addEventListener("input", function () {
        let amount = parseInt(this.value || 0);

        document.querySelectorAll(".membership-card")
            .forEach(c => c.classList.remove("active"));
        selectedPlan = null;

        // if (amount < 5000) {
        //     hidePreview();
        //     disablePay();
        //     return;
        // }

        if (amount < 1) {
            hidePreview();
            disablePay();
            return;
        }

        updatePreviewByAmount(amount);

        let plan = getMembershipByAmount(amount);
        if (!plan) return;

        let card = document.querySelector(
            `.membership-card[data-level="${plan.level}"]`
        );

        if (card) {
            card.classList.add("active");
            selectedPlan = card;
        }
    });

    payBtn.addEventListener("click", function () 
    {
        const amount = parseInt(amountInput.value || 0);

        /* ================= VALIDATION ================= */
        // if (amount < 5000) {
        //     $.toast({
        //         heading: "Error",
        //         text: "Minimum recharge amount is ₹5,000",
        //         position: "top-right",
        //         icon: "error"
        //     });
        //     return;
        // }

        if (amount < 1) {
            $.toast({
                heading: "Error",
                text: "Minimum recharge amount should not be less than 1",
                position: "top-right",
                icon: "error"
            });
            return;
        }

        payBtn.disabled = true;

        /* ================= CREATE ORDER ================= */
        const path = window.APP_URLS.create_wallet_order;
        const success_path = window.APP_URLS.payment_success;
        const failure_path = window.APP_URLS.payment_failed;

        fetch(path, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({
                amount: amount
            })
        })
        .then(res => res.json())
        .then(data => {

            if (!data.status) {
                $.toast({
                    heading: "Error",
                    text: data.message,
                    position: "top-right",
                    icon: "error"
                });
                payBtn.disabled = false;
                return;
            }

            /* ================= RAZORPAY OPTIONS ================= */
            const options = {
                key: data.key,
                amount: data.amount,          // paisa
                currency: "INR",
                name: "Digital Investment",
                description: "Wallet Recharge",
                order_id: data.order_id,
                config: {
                    display: {
                        blocks: {
                            upi: { name: "Pay via UPI", instruments: [{ method: "upi" }] },
                            other: { name: "Other Payment Methods", instruments: [{ method: "card" }, { method: "netbanking" }, { method: "wallet" }] }
                        },
                        sequence: ["block.upi", "block.other"],
                        preferences: { show_default_blocks: true }
                    }
                },

                handler: function (response) {
                    // ✅ PAYMENT SUCCESS → backend verification
                    const form = document.createElement("form");
                    form.method = "POST";
                    form.action = success_path;

                    addHidden(form, "razorpay_payment_id", response.razorpay_payment_id);
                    addHidden(form, "razorpay_order_id", response.razorpay_order_id);
                    addHidden(form, "razorpay_signature", response.razorpay_signature);
                    addHidden(form, "csrfmiddlewaretoken", getCSRFToken());

                    document.body.appendChild(form);
                    form.submit();
                },

                modal: {
                    ondismiss: function () {
                        // ❌ USER CLOSED POPUP
                        payBtn.disabled = false;
                        window.location.href =
                            failure_path +
                            "?order_id=" + data.order_id +
                            "&reason=" + encodeURIComponent("Payment cancelled by user");
                    }
                }
            };

            const rzp = new Razorpay(options);

            /* ================= PAYMENT FAILED EVENT ================= */
            rzp.on("payment.failed", function (response) {

                const reason =
                    response.error && response.error.description
                        ? response.error.description
                        : "Payment failed";

                window.location.href =
                    failure_path +
                    "?order_id=" + data.order_id +
                    "&reason=" + encodeURIComponent(reason);
            });

            rzp.open();
        })
        .catch(() => {
            $.toast({
                heading: "Error",
                text: "Something went wrong",
                position: "top-right",
                icon: "error"
            });
            payBtn.disabled = false;
        });
    });
    
    function addHidden(form, name, value) {
        const input = document.createElement("input");
        input.type = "hidden";
        input.name = name;
        input.value = value;
        form.appendChild(input);
    }

    /* ================= HELPERS ================= */

    function getMembershipByAmount(amount) {
        let matched = null;

        document.querySelectorAll(".membership-card").forEach(card => {
            const minAmount = parseInt(card.dataset.amount);

            if (amount >= minAmount) {
                matched = {
                    level: card.dataset.level,
                    fee: card.dataset.fee,
                    slots: card.dataset.slots,
                    amount: minAmount
                };
            }
        });

        return matched;
    }

    // function updatePreviewByAmount(amount) {
    //     let plan = getMembershipByAmount(amount);

    //     if (!plan) {
    //         hidePreview();
    //         disablePay();
    //         return;
    //     }

    //     updatePreview(plan);
    //     showPreview();
    //     enablePay();
    // }

    function updatePreviewByAmount(amount) {
        let plan = getMembershipByAmount(amount);

        if (!plan) {
            // 👉 NEW FIX
            showPreview();   // optional (ya hide bhi kar sakti ho)
            document.getElementById("pLevel").innerText = "No Change";
            document.getElementById("pFee").innerText = "-";
            document.getElementById("pSlots").innerText = "-";

            enablePay();   // ✅ button enable karo
            return;
        }

        updatePreview(plan);
        showPreview();
        enablePay();
    }

    function updatePreview(plan) {
        document.getElementById("pLevel").innerText = plan.level;
        document.getElementById("pFee").innerText = `₹${plan.fee}/-`;
        document.getElementById("pSlots").innerText = `${plan.slots} slots/day`;
    }

    function showPreview() {
        document.getElementById("membershipPreview").style.display = "block";
    }

    function hidePreview() {
        document.getElementById("membershipPreview").style.display = "none";
    }

    function disablePay() {
        payBtn.disabled = true;
        payBtn.classList.add("disabled");
    }

    function enablePay() {
        payBtn.disabled = false;
        payBtn.classList.remove("disabled");
    }
});