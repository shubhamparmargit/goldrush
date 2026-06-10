const overlay = document.getElementById("overlay");
const sheet = document.getElementById("bottomSheet");

function openSheet() {
    overlay.classList.add("active");
    sheet.classList.add("active");
}

function closeSheet() {
    overlay.classList.remove("active");
    sheet.classList.remove("active");
}

overlay.addEventListener("click", closeSheet);
document.getElementById("closeSheetBtn").addEventListener("click", closeSheet);

function openHistorySheet(item) {

    const orderId = item.dataset.id;
    const path = window.APP_URLS.wallet_history_detail; 
    fetch(`${path}?order_id=${orderId}`)
        .then(res => res.json())
        .then(data => {

            if (!data.status) {
                $.toast({
                    heading: "Error",
                    text: data.message,
                    position: "top-right",
                    icon: "error"
                });
                return;
            }

            document.getElementById("sheetTitle").innerText = "Transaction Details";

            document.getElementById("sheetContent").innerHTML = `
                <div class="sheet-row"><span>Transaction ID</span><span>${data.txn_id}</span></div>
                <div class="sheet-row"><span>Type</span><span>${data.type}</span></div>
                <div class="sheet-row"><span>Amount</span><span>₹${data.amount}</span></div>
                <div class="sheet-row">
                    <span>Status</span>
                    <span class="status-pill ${data.status === "Success" ? "status-success" : "status-danger"}">
                        ${data.status}
                    </span>
                </div>
                <div class="sheet-row"><span>Date</span><span>${data.date}</span></div>
                <div class="sheet-row"><span>Gateway</span><span>${data.gateway}</span></div>
                <div class="sheet-row"><span>Membership</span><span>${data.membership}</span></div>
                <div class="sheet-row"><span>Balance After</span><span>₹${data.balance}</span></div>
            `;

            openSheet();
        })
        .catch(() => {
            $.toast({
                heading: "Error",
                text: "Something went wrong",
                position: "top-right",
                icon: "error"
            });
        });
}

function openGoldSheet(gm, metal_type) {
    let AUTO_SELL_BASE_AMOUNT = 0;
    const path = window.APP_URLS.order_calculation;

    fetch(`${path}?gm=${gm}&metal_type=${metal_type}`)
        .then(res => res.json())
        .then(data => {

            if (!data.status) {
                $.toast({
                    heading: "Error",
                    text: data.message,
                    position: "top-right",
                    icon: "error"
                });
                return;
            }

            AUTO_SELL_BASE_AMOUNT = Number(data.market_amount);

            const title = metal_type === 'gold' ? "Gold Purchase" : "Silver Purchase";

            document.getElementById("sheetTitle").innerText = title;

            document.getElementById("sheetContent").innerHTML = `
                <!-- ORDER DETAILS -->
                <div class="sheet-row">
                    <span>Quantity</span>
                    <span>${gm} gm</span>
                </div>

                <div class="sheet-row">
                    <span>Order Amount</span>
                    <span>₹${data.order_amt}</span>
                </div>

                <!-- SERVICE FEE BREAKUP -->
                <div class="sheet-divider">Service Fee Breakup</div>

                <div class="sheet-row">
                    <span>Service Fee</span>
                    <span>₹${data.service_fee}</span>
                </div>

                <div class="sheet-row sub">
                    <span>GST (18%)</span>
                    <span>₹${data.gst}</span>
                </div>

                <div class="sheet-row sub">
                    <span>Reward</span>
                    <span>₹${data.reward}</span>
                </div>

                <div class="sheet-row">
                    <span>Actual Service Fee</span>
                    <span>₹${data.actual_service_fee}</span>
                </div>

                <!-- FINAL -->
                <div class="sheet-row total">
                    <span>Market Amount</span>
                    <span>₹${data.market_amount}</span>
                </div>

                <div class="auto-sell-box">
                    <div class="auto-sell-header">
                        <span>Auto Sell<small>(optional)</small></span>

                        <span id="autoSellPercentBadge" class="auto-sell-percent neutral">0%</span>
                        
                        <!-- ✅ ADD ONLY -->
                        <label class="auto-sell-toggle">
                            <input type="checkbox" id="autoSellToggle">
                            <span class="toggle-slider"></span>
                        </label>
                    </div>

                    <div class="auto-sell-input-wrap">
                        <button type="button" class="auto-btn" id="autoSellMinus">−</button>

                        <input type="number"
                            id="autoSellAmount"
                            class="auto-sell-input"
                            step="1" value="${data.market_amount}">

                        <button type="button" class="auto-btn" id="autoSellPlus">+</button>
                    </div>

                    <div class="auto-sell-hint">
                        Order will auto close at this total value (profit or loss)
                    </div>
                </div>

                <div class="sheet-row">
                    <button class="action-btn primary-btn w-100" id="confirmMetalBuy">
                        Buy
                    </button>
                    <button class="action-btn buyback-btn w-100" id="confirmMetalBuyBack">
                        Sell
                    </button>
                </div>

            `;

            openSheet();
        })
        .catch(err => {
            // console.error("ERROR:", err);
            // alert("Error: " + err.message);
            $.toast({
                heading: "Error",
                text: "Something went wrong",
                position: "top-right",
                icon: "error"
            });
        });

    setTimeout(() => {
        const buyBtn = document.getElementById("confirmMetalBuy");
        const buybackBtn = document.getElementById("confirmMetalBuyBack");
        const toggle = document.getElementById("autoSellToggle");
        const autoSellAmount = document.getElementById("autoSellAmount");
        initAutoSellUI("autoSellToggle", "autoSellAmount", "autoSellPlus", "autoSellMinus", ".auto-sell-input-wrap", AUTO_SELL_BASE_AMOUNT)

        updateAutoSellPercentDisplay("autoSellAmount", AUTO_SELL_BASE_AMOUNT);

        if (buyBtn) {
            buyBtn.onclick = () => {
                const enabled = toggle && toggle.checked;
                const amount = enabled ? autoSellAmount.value : null;
                placeOrder("BOOKING", buyBtn, gm, metal_type, amount, enabled);
            };
        }

        if (buybackBtn) {
            buybackBtn.onclick = () => {
                const enabled = toggle && toggle.checked;
                const amount = enabled ? autoSellAmount.value : null;
                placeOrder("BUYBACK", buybackBtn, gm, metal_type, amount, enabled);
            };
        }

    }, 100);
}

function placeOrder(type, btn, gm, metal_type, autoSellAmount, autoSellEnabled) {
    btn.disabled = true;
    const path = window.APP_URLS.buy_metal;

    showLoader();

    setTimeout(() => {
        fetch(path, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({
                gm: gm,
                order_type: type,    // 🔥 BUY or SELL
                metal_type: metal_type,    // 🔥 Gold or Silver
                auto_sell_amount: autoSellAmount,
                auto_sell_enabled: autoSellEnabled,
            })
        })
        .then(res => res.json())
        .then(data => {
            hideLoader();

            if (!data.status) {
                $.toast({
                    heading: "Error",
                    text: data.message,
                    position: "top-right",
                    icon: "error"
                });
                btn.disabled = false;
                return;
            }

            $.toast({
                heading: "Success",
                text: type === "BOOKING" ? "Booking placed" : "Buyback placed",
                icon: "success",
                position: "top-right"
            });

            document.getElementById("walletBalance").innerText = "₹" + Number(data.wallet_balance).toLocaleString("en-IN");

            closeSheet();
        })
        .catch(err => {
            // console.error("ERROR:", err);
            // alert("Error: " + err.message);
            hideLoader();
            $.toast({
                heading: "Error",
                text: "Something went wrong",
                position: "top-right",
                icon: "error"
            });
            btn.disabled = false;
        });
    },3000);
}

function openTransactionSheet(item) {

    const transaction_id = item.dataset.id;

    if (!transaction_id) {
        $.toast({
            heading: "Error",
            text: "Invalid transaction",
            position: "top-right",
            icon: "error"
        });
        return;
    }

    let AUTO_SELL_BASE_AMOUNT = 0;
    const path = window.APP_URLS.live_order_details;

    fetch(`${path}?transaction_id=${transaction_id}`)
        .then(res => res.json())
        .then(data => {

            if (!data.status) {
                $.toast({
                    heading: "Error",
                    text: data.message,
                    position: "top-right",
                    icon: "error"
                });
                return;
            }

            const orderTypeText =
                data.order_type === "BOOKING"
                    ? "Booking Order – Profit when market goes UP"
                    : "Buyback Order – Profit when market goes DOWN";

            const orderTypeClass =
                data.order_type === "BOOKING" ? "booking" : "buyback";

            // console.log(data.auto_sell_enabled, typeof data.auto_sell_enabled);

            AUTO_SELL_BASE_AMOUNT = Number(data.market_amount);
            // console.log("AUTO_SELL_BASE_AMOUNT :: "+AUTO_SELL_BASE_AMOUNT)

            document.getElementById("sheetTitle").innerText = "Live Order Details";

            document.getElementById("sheetContent").innerHTML = `
                <div class="sheet-highlight ${orderTypeClass}">${orderTypeText}</div>
                <div class="sheet-row"><span>Metal</span><span>${data.metal_type}</span></div>
                <div class="sheet-row"><span>Quantity</span><span>${data.quantity} gm</span></div>

                <div class="sheet-divider">Buy Details</div>

                <div class="sheet-row"><span>Buy Rate</span><span>${data.currency_icon}${data.buy_rate}</span></div>
                <div class="sheet-row"><span>Invested</span><span>₹${data.invested_amount}</span></div>
                <div class="sheet-row"><span>Service Fee</span><span>₹${data.service_fee}</span></div>
                <!-- <div class="sheet-row"><span>Actual Metal Invested</span><span>₹${data.market_amount}</span></div> -->
                <div class="sheet-row"><span>Date</span><span>${data.buy_date}</span></div>

                <div class="sheet-divider">Current Value</div>

                <div class="sheet-row"><span>Current Rate</span><span>${data.currency_icon}${data.current_metal_rate}</span></div>
                <div class="sheet-row total">
                    <span>Current Invested Value</span>
                    <span>₹${data.current_value}</span>
                </div>

                <div class="sheet-row price-grid" style="margin-bottom: 0 !important;">
                    <span>Difference</span>
                    <span class="${data.is_profit ? 'profit' : 'loss'}">
                        <b>${data.is_profit ? '+' : '-'}${Math.abs(data.difference)} Points</b>
                    </span>
                </div>

                <!--<div class="sheet-row price-grid">
                    <span>P/L</span>
                    <span class="${data.is_profit ? 'profit' : 'loss'}">
                        <b>${data.is_profit ? '+' : '-'}₹${Math.abs(data.pnl_amount)}
                        (${Math.abs(data.pnl_percent)}%)</b>
                    </span>
                </div>-->
                <div class="sheet-row price-grid">
                    <span>P/L</span>
                    <span class="${data.is_profit ? 'profit' : 'loss'}">
                        <b>${data.is_profit ? '+' : '-'}₹${Math.abs(data.pnl_amount)}</b>
                    </span>
                </div>

                <div class="auto-sell-box auto-sell-edit">
                    <div class="auto-sell-header">
                        <span>Auto Sell <small>(edit)</small></span>
                    
                        <span id="autoSellPercentBadge" class="auto-sell-percent neutral">0%</span>

                        <label class="auto-sell-toggle">
                            <input type="checkbox" id="editAutoSellToggle"
                                ${data.auto_sell_enabled ? 'checked' : ''}>
                            <span class="toggle-slider"></span>
                        </label>
                    </div>

                    <div class="auto-sell-input-wrap 
                        ${!data.auto_sell_enabled ? 'auto-sell-disabled' : ''}">
                        
                        <button type="button" class="auto-btn" id="editAutoSellMinus">−</button>

                        <input type="number"
                            id="editAutoSellAmount"
                            class="auto-sell-input"
                            value="${data.auto_sell_amount || data.market_amount}"
                            ${!data.auto_sell_enabled ? 'disabled' : ''}>

                        <button type="button" class="auto-btn" id="editAutoSellPlus">+</button>
                    </div>

                    <div class="sheet-row mt-2">
                        <div class="auto-sell-hint">
                            Order will auto close at this total value
                        </div>
                        <button class="action-btn btn-outline" style="width:auto;" id="saveAutoSellBtn" data-id="${data.transaction_id}"> Save </button>
                    </div>
                </div>
            `;

            openSheet();
        })
        .catch(() => {
            $.toast({
                heading: "Error",
                text: "Something went wrong",
                position: "top-right",
                icon: "error"
            });
        });

    setTimeout(() => {
        const saveBtn = document.getElementById("saveAutoSellBtn");
        const toggle = document.getElementById("editAutoSellToggle");
        const input = document.getElementById("editAutoSellAmount");

        initAutoSellUI("editAutoSellToggle", "editAutoSellAmount", "editAutoSellPlus", "editAutoSellMinus", ".auto-sell-input-wrap", AUTO_SELL_BASE_AMOUNT)
        
        // console.log("AUTO_SELL_BASE_AMOUNT :: "+AUTO_SELL_BASE_AMOUNT)
        updateAutoSellPercentDisplay("editAutoSellAmount", AUTO_SELL_BASE_AMOUNT);

        if (saveBtn) {
            saveBtn.onclick = () => {
                const autoSellEnabled = toggle.checked;
                const autoSellAmount = autoSellEnabled ? input.value : null;

                if (autoSellEnabled && (!autoSellAmount || autoSellAmount <= 0)) {
                    $.toast({
                        heading: "Error",
                        text: "Invalid auto sell amount",
                        icon: "error",
                        position: "top-right"
                    });
                    return;
                }

                const path_sell = window.APP_URLS.update_auto_sell;
                fetch(path_sell, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken()
                    },
                    body: JSON.stringify({
                        transaction_id: saveBtn.dataset.id,
                        auto_sell_enabled: autoSellEnabled,
                        auto_sell_amount: autoSellAmount
                    })
                })
                .then(res => res.json())
                .then(data => {
                    if (!data.status) {
                        $.toast({
                            heading: "Error",
                            text: data.message,
                            icon: "error",
                            position: "top-right"
                        });
                        return;
                    }

                    $.toast({
                        heading: "Success",
                        text: "Auto Sell updated",
                        icon: "success",
                        position: "top-right"
                    });

                    closeSheet();
                });
            };
        }
    }, 100);

}

function initAutoSellUI(toggleId, inputId, plusId, minusId, wrapSelector, AUTO_SELL_BASE_AMOUNT) {
    const toggle = document.getElementById(toggleId);
    const autoSellAmount = document.getElementById(inputId);
    const wrap = document.querySelector(wrapSelector);

    const plusBtn = document.getElementById(plusId);
    const minusBtn = document.getElementById(minusId);

    if (toggle) {
        // 🔒 Default OFF
        if (!toggle.checked) {
            autoSellAmount.disabled = true;
            wrap.classList.add("auto-sell-disabled");
        } else {
            autoSellAmount.disabled = false;
            wrap.classList.remove("auto-sell-disabled");
        }

        toggle.addEventListener("change", function () {
            updateAutoSellPercentDisplay(inputId, AUTO_SELL_BASE_AMOUNT);
            if (this.checked) {
                autoSellAmount.disabled = false;
                wrap.classList.remove("auto-sell-disabled");
            } else {
                autoSellAmount.disabled = true;
                wrap.classList.add("auto-sell-disabled");
            }
        });
    }

    if (autoSellAmount) {
        const STEP = 1; // ₹1 step (chaaho to 5 / 10 bhi kar sakti ho)

        plusBtn.onclick = () => {
            autoSellAmount.value = Number(autoSellAmount.value) + STEP;
            updateAutoSellPercentDisplay(inputId, AUTO_SELL_BASE_AMOUNT);
        };

        minusBtn.onclick = () => {
            const newVal = Number(autoSellAmount.value) - STEP;
            autoSellAmount.value = newVal > 0 ? newVal : 0;
            updateAutoSellPercentDisplay(inputId, AUTO_SELL_BASE_AMOUNT);
        };
    }
}

function updateAutoSellPercentDisplay(inputId, AUTO_SELL_BASE_AMOUNT) {
    // console.log("AUTO_SELL_BASE_AMOUNT :: "+AUTO_SELL_BASE_AMOUNT)
    const badge = document.getElementById("autoSellPercentBadge");
    const input = document.getElementById(inputId);

    if (!badge || !input || !AUTO_SELL_BASE_AMOUNT) return;

    const current = Number(input.value);
    if (!current) return;

    const percent = ((current - AUTO_SELL_BASE_AMOUNT) / AUTO_SELL_BASE_AMOUNT) * 100;
    const abs = Math.abs(percent).toFixed(2);

    if (percent > 0) {
        badge.textContent = `+${abs}%`;
        badge.className = "auto-sell-percent green";
        badge.style.display = "inline";
    } else if (percent < 0) {
        badge.textContent = `-${abs}%`;
        badge.className = "auto-sell-percent red";
        badge.style.display = "inline";
    } else {
        // badge.textContent = "0%";
        // badge.className = "auto-sell-percent neutral";
        badge.textContent = "";
        badge.style.display = "none";
    }
}

function openSellConfirmSheet(transactionId) {
    document.getElementById("sheetTitle").innerText = "Confirm to Order Cancel";

    document.getElementById("sheetContent").innerHTML = `
        <div class="sheet-row">
            <span>Are you sure you want to cancel this order?</span>
        </div>

        <div class="sheet-row total">
            <span>This will settle at current market price</span>
        </div>

        <div class="sheet-row mt-2">
            <button class="action-btn primary-btn w-100" id="confirmSellBtn">
                Confirm
            </button>
            <button class="action-btn btn-outline w-100" id="cancelSellBtn">
                Cancel
            </button>
        </div>
    `;

    openSheet();

    document.getElementById("confirmSellBtn").onclick = function () {
        closeSheet();
        executeSell(transactionId);
    };

    document.getElementById("cancelSellBtn").onclick = closeSheet;
}

function executeSell(transactionId) {
    const transaction_id = transactionId;

    if (!transaction_id) {
        $.toast({
            heading: "Error",
            text: "Invalid request",
            position: "top-right",
            icon: "error"
        });
        return;
    }

    const path = window.APP_URLS.sell_metal;

    showLoader();

    setTimeout(() => {
        fetch(path, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({
                transaction_id: transaction_id
            })
        })
            .then(res => res.json())
            .then(data => {
                hideLoader();
                if (!data.status) {
                    $.toast({
                        heading: "Error",
                        text: data.message,
                        position: "top-right",
                        icon: "error"
                    });
                    return;
                }

                $.toast({
                    heading: "Success",
                    text: "Metal sold successfully",
                    position: "top-right",
                    icon: "success"
                });

                // 🔄 reload to refresh live orders
                setTimeout(() => {
                    location.reload();
                }, 800);

            })
            .catch(() => {
                hideLoader();
                $.toast({
                    heading: "Error",
                    text: "Something went wrong",
                    position: "top-right",
                    icon: "error"
                });
            });
    },3000);

}

function openPastOrderSheet(item) {

    const transaction_id = item.dataset.id;

    if (!transaction_id) {
        $.toast({
            heading: "Error",
            text: "Invalid transaction",
            position: "top-right",
            icon: "error"
        });
        return;
    }

    const path = window.APP_URLS.past_order_details;
    fetch(`${path}?transaction_id=${transaction_id}`)
        .then(res => res.json())
        .then(data => {

            if (!data.status) {
                $.toast({
                    heading: "Error",
                    text: data.message,
                    position: "top-right",
                    icon: "error"
                });
                return;
            }

            let soldViaHtml = `
                <div class="sheet-row">
                    <span>Sold Via</span>
                    <span class="${data.is_auto_sold ? 'profit' : ''}">
                        ${data.is_auto_sold ? 'Auto Sell' : 'Manual Sell'}
                    </span>
                </div>
            `;

            let autoSellHtml = '';

            if (data.is_auto_sold) {
                autoSellHtml = `
                    <div class="sheet-row">
                        <span>Auto Sell Amount</span>
                        <span>₹${data.auto_sell_amount}</span>
                    </div>
                `;
            }

            document.getElementById("sheetTitle").innerText = "Past Order Details";

            document.getElementById("sheetContent").innerHTML = `
                <div class="sheet-row">
                    <span>Metal</span>
                    <span>${data.metal_type}</span>
                </div>

                <div class="sheet-row">
                    <span>Quantity</span>
                    <span>${data.quantity} gm</span>
                </div>

                <div class="sheet-divider">Buy Details</div>

                <div class="sheet-row">
                    <span>Buy Rate</span>
                    <span>${data.currency_icon}${data.buy_rate}</span>
                </div>

                <div class="sheet-row">
                    <span>Invested Amount</span>
                    <span>₹${data.invested_amount}</span>
                </div>

                <div class="sheet-row"><span>Service Fee</span><span>₹${data.service_fee}</span></div>
                <!-- <div class="sheet-row"><span>Actual Metal Invested</span><span>₹${data.market_amount}</span></div> -->

                <div class="sheet-row">
                    <span>Buy Date</span>
                    <span>${data.buy_date}</span>
                </div>

                <div class="sheet-divider">Sell Details</div>

                <div class="sheet-row">
                    <span>Sell Rate</span>
                    <span>${data.currency_icon}${data.sell_rate}</span>
                </div>

                <!-- <div class="sheet-row">
                    <span>Sell Amount</span>
                    <span>₹${data.sell_amount}</span>
                </div> -->

                <div class="sheet-row">
                    <span>Sell Date</span>
                    <span>${data.sell_date}</span>
                </div>

                <div class="sheet-divider">Order Info</div>

                ${soldViaHtml}
                ${autoSellHtml}

                <div class="sheet-divider">Profit / Loss</div>

                <div class="sheet-row">
                    <span>Order Type</span>
                    <span class="order-type ${data.order_type === "BOOKING" ? "booking" : "buyback"}">
                        ${data.order_type}
                    </span>
                </div>

                <!--<div class="sheet-row price-grid">
                    <span>P/L</span>
                    <span class="${data.is_profit ? 'profit' : 'loss'}">
                        <b>${data.is_profit ? '+' : '-'}₹${Math.abs(data.pnl_amount)}
                        (${Math.abs(data.pnl_percent)}%)</b>
                    </span>
                </div>-->

                <div class="sheet-row price-grid">
                    <span>P/L</span>
                    <span class="${data.is_profit ? 'profit' : 'loss'}">
                        <b>${data.is_profit ? '+' : '-'}₹${Math.abs(data.pnl_amount)}</b>
                    </span>
                </div>
            `;

            openSheet();
        })
        .catch(() => {
            $.toast({
                heading: "Error",
                text: "Something went wrong",
                position: "top-right",
                icon: "error"
            });
        });
}

function openWithdrawalSheet() {
    if (window.HAS_BANK_DETAILS) {
        openWithdrawalAmountSheet();
    } else {
        openBankDetailsSheet();
    }
}

function openBankDetailsSheet() {
    document.getElementById("sheetTitle").innerText = "Bank Details";

    document.getElementById("sheetContent").innerHTML = `
        <div class="sheet-divider">Account Details</div>
        <div class="sheet-row">
            <input type="text" id="wd_account_holder_name" class="form-control" placeholder="Account Holder Name *">
        </div>
        <div class="sheet-row">
            <input type="number" id="wd_account_number" class="form-control" placeholder="Account Number *">
        </div>
        <div class="sheet-row">
            <input type="text" id="wd_ifsc_code" class="form-control" placeholder="IFSC Code *">
        </div>
        <div class="sheet-row mt-2">
            <input type="email" id="wd_email" class="form-control" placeholder="Email ID *">
        </div>

        <div class="sheet-divider">Bank Document</div>
        <div class="sheet-row">
            <label class="f14-regular mb-6 d-block">Select Document Type *</label>
            <select id="wd_bank_doc_type" class="form-control" style="background-color: #fff; border: 1px solid #ccc; padding: 10px 30px 10px 10px; border-radius: 8px; width: 100%; appearance: none; -webkit-appearance: none; -moz-appearance: none; background: url('data:image/svg+xml;utf8,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 24 24%22 fill=%22%23666%22><path d=%22M7 10l5 5 5-5z%22/></svg>') no-repeat right 12px center/18px;">
                <option value="cancelled_cheque">Cancelled Cheque</option>
                <option value="passbook">Passbook</option>
            </select>
        </div>
        <div class="sheet-row" id="cancelled_cheque_row">
            <label class="f14-regular mb-6 d-block">Upload Cancelled Cheque *</label>
            <input type="file" id="wd_cancelled_cheque" class="form-control" accept=".jpg,.jpeg,.png,.pdf">
        </div>
        <div class="sheet-row" id="passbook_row" style="display: none;">
            <label class="f14-regular mb-6 d-block">Upload Passbook *</label>
            <input type="file" id="wd_passbook" class="form-control" accept=".jpg,.jpeg,.png,.pdf">
        </div>

        <div class="sheet-divider">Aadhaar Card</div>
        <div class="sheet-row">
            <label class="f14-regular mb-6 d-block">Aadhaar Front *</label>
            <input type="file" id="wd_aadhaar_front" class="form-control" accept=".jpg,.jpeg,.png,.pdf">
        </div>
        <div class="sheet-row">
            <label class="f14-regular mb-6 d-block">Aadhaar Back *</label>
            <input type="file" id="wd_aadhaar_back" class="form-control" accept=".jpg,.jpeg,.png,.pdf">
        </div>

        <div class="sheet-divider">PAN Card</div>
        <div class="sheet-row">
            <label class="f14-regular mb-6 d-block">PAN Front *</label>
            <input type="file" id="wd_pan_front" class="form-control" accept=".jpg,.jpeg,.png,.pdf">
        </div>
        <div class="sheet-row">
            <label class="f14-regular mb-6 d-block">PAN Back *</label>
            <input type="file" id="wd_pan_back" class="form-control" accept=".jpg,.jpeg,.png,.pdf">
        </div>

        <div class="sheet-row mt-2">
            <button class="action-btn btn-outline w-100" id="cancelBankDetails">Cancel</button>
            <button class="action-btn primary-btn w-100" id="submitBankDetails">Next</button>
        </div>
    `;

    openSheet();

    setTimeout(() => {
        document.getElementById("cancelBankDetails").onclick = closeSheet;
        document.getElementById("submitBankDetails").onclick = submitBankDetailsForWithdrawal;

        const docTypeSelect = document.getElementById("wd_bank_doc_type");
        const chequeRow = document.getElementById("cancelled_cheque_row");
        const passbookRow = document.getElementById("passbook_row");
        
        docTypeSelect.addEventListener("change", function() {
            if (this.value === "cancelled_cheque") {
                chequeRow.style.display = "block";
                passbookRow.style.display = "none";
                document.getElementById("wd_passbook").value = "";
            } else {
                chequeRow.style.display = "none";
                passbookRow.style.display = "block";
                document.getElementById("wd_cancelled_cheque").value = "";
            }
        });
    }, 100);
}

function submitBankDetailsForWithdrawal() {
    const btn = document.getElementById("submitBankDetails");

    const accountHolderName = document.getElementById("wd_account_holder_name").value.trim();
    const accountNumber = document.getElementById("wd_account_number").value.trim();
    const ifscCode = document.getElementById("wd_ifsc_code").value.trim();
    const email = document.getElementById("wd_email").value.trim();
    const docType = document.getElementById("wd_bank_doc_type").value;
    const cancelledCheque = document.getElementById("wd_cancelled_cheque").files[0];
    const passbook = document.getElementById("wd_passbook").files[0];
    const aadhaarFront = document.getElementById("wd_aadhaar_front").files[0];
    const aadhaarBack = document.getElementById("wd_aadhaar_back").files[0];
    const panFront = document.getElementById("wd_pan_front").files[0];
    const panBack = document.getElementById("wd_pan_back").files[0];

    if (!accountHolderName) { showError("Account holder name is required"); return; }
    if (!accountNumber) { showError("Account number is required"); return; }
    if (!/^[0-9]+$/.test(accountNumber)) { showError("Enter a valid account number"); return; }
    if (!ifscCode) { showError("IFSC code is required"); return; }
    if (!/^[A-Za-z]{4}0[A-Z0-9a-z]{6}$/.test(ifscCode)) { showError("Enter a valid IFSC code"); return; }
    if (!email) { showError("Email ID is required"); return; }
    if (!/[^@]+@[^@]+\.[^@]+/.test(email)) { showError("Please enter a valid email ID"); return; }
    
    if (docType === "cancelled_cheque" && !cancelledCheque) {
        showError("Cancelled Cheque upload is required");
        return;
    }
    if (docType === "passbook" && !passbook) {
        showError("Passbook upload is required");
        return;
    }
    if (!aadhaarFront) { showError("Aadhaar front photo is required"); return; }
    if (!aadhaarBack) { showError("Aadhaar back photo is required"); return; }
    if (!panFront) { showError("PAN front photo is required"); return; }
    if (!panBack) { showError("PAN back photo is required"); return; }

    const formData = new FormData();
    formData.append("bank_name", "");
    formData.append("account_holder_name", accountHolderName);
    formData.append("account_number", accountNumber);
    formData.append("ifsc_code", ifscCode);
    formData.append("email", email);
    formData.append("branch_name", "");
    if (cancelledCheque) formData.append("cancelled_cheque", cancelledCheque);
    if (passbook) formData.append("passbook", passbook);
    formData.append("aadhaar_front", aadhaarFront);
    formData.append("aadhaar_back", aadhaarBack);
    formData.append("pan_front", panFront);
    formData.append("pan_back", panBack);
    formData.append("csrfmiddlewaretoken", getCSRFToken());

    btn.disabled = true;
    showLoader();

    fetch(window.SAVE_BANK_URL, {
        method: "POST",
        headers: { "X-CSRFToken": getCSRFToken() },
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        hideLoader();
        btn.disabled = false;

        if (data.success != 1) {
            const msg = data.errors ? Object.values(data.errors)[0] : data.message;
            showError(msg || "Something went wrong");
            return;
        }

        window.HAS_BANK_DETAILS = true;
        openWithdrawalAmountSheet();
    })
    .catch(() => {
        hideLoader();
        btn.disabled = false;
        showError("Something went wrong");
    });
}

function openWithdrawalAmountSheet() {
    const closingBalance = document.getElementById("walletBalance").innerText || "0";

    document.getElementById("sheetTitle").innerText = "Withdrawal Request";

    document.getElementById("sheetContent").innerHTML = `
        <div class="sheet-row">
            <span>Closing Balance</span>
            <span>${closingBalance}</span>
        </div>

        <div class="sheet-divider">Enter Withdrawal Details</div>

        <div class="sheet-row">
            <input type="number"
                   id="withdrawAmount"
                   class="form-control"
                   placeholder="Enter amount *"
                   min="1">
        </div>

        <div class="sheet-row mt-2">
            <input type="email"
                   id="withdrawEmail"
                   class="form-control"
                   placeholder="Enter Email ID *"
                   style="width: 100%;">
        </div>

        <div class="sheet-row mt-2">
            <button class="action-btn btn-outline w-100" id="cancelWithdraw">Cancel</button>
            <button class="action-btn primary-btn w-100" id="confirmWithdraw">Withdraw</button>
        </div>
    `;

    openSheet();

    setTimeout(() => {
        document.getElementById("cancelWithdraw").onclick = closeSheet;

        document.getElementById("confirmWithdraw").onclick = function () {
            const amount = parseFloat(document.getElementById("withdrawAmount").value);
            const email = document.getElementById("withdrawEmail").value.trim();
            const balanceText = document.getElementById("walletBalance").innerText;
            const closingBalance = parseFloat(balanceText.replace(/[₹,\/-]/g, ''));

            if (!amount || amount <= 0) { showError("Enter valid amount"); return; }
            if (amount > closingBalance) { showError("Amount cannot exceed closing balance"); return; }
            if (amount < 100) { showError("Minimum withdrawal is ₹100"); return; }
            if (!email) { showError("Email ID is required"); return; }
            if (!/[^@]+@[^@]+\.[^@]+/.test(email)) { showError("Please enter a valid email ID"); return; }

            submitWithdrawal(amount, email);
        };

        const input = document.getElementById("withdrawAmount");
        if (input) {
            input.addEventListener("input", function () {
                const amount = parseFloat(this.value);
                const balance = parseFloat(
                    document.getElementById("walletBalance").innerText.replace(/[₹,\/-]/g, '')
                );
                this.style.border = amount > balance ? "2px solid red" : "1px solid #ccc";
            });
        }
    }, 100);
}

function showError(msg) {
    $.toast({
        heading: "Error",
        text: msg,
        icon: "error",
        position: "top-right"
    });
}

function submitWithdrawal(amount, email) {

    const path = window.APP_URLS.withdraw_request;

    const btn = document.getElementById("confirmWithdraw");
    btn.disabled = true;

    showLoader();

    fetch(path, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({
            amount: amount,
            email: email
        })
    })
    .then(res => res.json())
    .then(data => {

        hideLoader();
        btn.disabled = false;

        if (!data.status) {
            $.toast({
                heading: "Error",
                text: data.message,
                icon: "error",
                position: "top-right"
            });
            return;
        }

        // ✅ SUCCESS
        $.toast({
            heading: "Success",
            text: "Withdrawal request submitted successfully",
            icon: "success",
            position: "top-right"
        });

        // 🔥 Wallet balance update (important)
        if (data.wallet_balance !== undefined) {
            document.getElementById("walletBalance").innerText =
                "₹" + Number(data.wallet_balance).toLocaleString("en-IN") + "/-";
        }

        closeSheet();

        loadWithdrawalList();

    })
    .catch(() => {
        hideLoader();
        btn.disabled = false;

        $.toast({
            heading: "Error",
            text: "Something went wrong",
            icon: "error",
            position: "top-right"
        });
    });
}

function loadWithdrawalList() {

    const path = window.APP_URLS.withdraw_history;

    fetch(path)
        .then(res => res.json())
        .then(data => {

            if (!data.status) return;

            let html = "";

            data.data.forEach(w => {

                html += `
                <div class="withdraw-card">

                    <div class="card-header">
                        <div>
                            <div class="title">Withdrawal</div>
                            <div class="date">${w.request_date_full}</div>
                        </div>
                        <div class="amount">
                            ₹${Number(w.amount).toLocaleString("en-IN")}
                        </div>
                    </div>

                    <div class="divider"></div>

                    <div class="card-body">

                        <div class="row">
                            <span>Status</span>
                            <span class="status ${w.status_class}">
                                ${w.status}
                            </span>
                        </div>

                        <div class="row">
                            <span>Service Charge</span>
                            <span>₹${w.service_charge}</span>
                        </div>

                        <div class="row">
                            <span>GST (18%)</span>
                            <span>₹${w.gst}</span>
                        </div>

                        <div class="row total">
                            <span>Final Amount</span>
                            <span>₹${w.final_amount}</span>
                        </div>

                        <div class="row">
                            <span>Requested On</span>
                            <span>${w.request_date}</span>
                        </div>

                        ${w.action_date ? `
                        <div class="row">
                            <span>Processed On</span>
                            <span>${w.action_date}</span>
                        </div>` : ''}

                        ${w.txn ? `
                        <div class="row">
                            <span>Transaction No</span>
                            <span class="txn">${w.txn}</span>
                        </div>` : ''}

                        ${w.remark ? `
                        <div class="row">
                            <span>Remark</span>
                            <span class="remark">${w.remark}</span>
                        </div>` : ''}

                    </div>

                </div>
                `;
            });

            document.getElementById("withdrawalList").innerHTML = html;

        });
}