'use strict'

let totalForm

let orderTotalQuantity, orderTotalCost, orderQuantityDOM, orderTotalCostDOM

let orderItemNum, orderItemQuantity
let quantityArr = []
let priceArr = []
let totalPriceArr = []


let productQuantity, productPrice, deltaQuantity, deltaCost, productTotalCost

let $orderForm


function renderSummary(quantity, totalCost){
    orderQuantityDOM.html(quantity.toString());
    orderTotalCostDOM.html(Number(totalCost.toFixed(2)).toString().replace('.', ','));
}


function renderTotalCostItem(num){
    let item = $('.items-' + num + '-total_price')
    productTotalCost = (quantityArr[num] * priceArr[num]);
    item.html(Number(productTotalCost.toFixed(2)).toString().replace('.', ','));
}


function updateTotalQuantity(){
    orderTotalQuantity = 0;
    orderTotalCost = 0;

    for (let i = 0; i < totalForm; i++){
            orderTotalQuantity += quantityArr[i];
            orderTotalCost += quantityArr[i] * priceArr[i];
        }
        renderSummary(orderTotalQuantity, orderTotalCost)
}


function orderSummaryUpdate(price, delta, ){
    orderTotalQuantity +=delta;
    deltaCost = price * deltaQuantity;
    orderTotalCost += deltaCost;
    renderSummary(orderTotalQuantity, orderTotalCost)
}


function deleteOrderItem(row) {
    let targetName = row[0].querySelector('input[type="number"]').name;
    orderItemNum = parseInt(targetName.replace('order-', '').replace('-quantity', ''));
    deltaQuantity = -quantityArr[orderItemNum];
    orderSummaryUpdate(priceArr[orderItemNum], deltaQuantity);
}


window.onload = function () {
    totalForm = parseInt($('input[name="order-TOTAL_FORMS"]').val());
    orderQuantityDOM = $('.order_total_quantity');
    orderTotalQuantity = parseInt(orderQuantityDOM.text()) || 0;
    orderTotalCostDOM = $('.order_total_cost')
    orderTotalCost = parseFloat(orderTotalCostDOM.text().replace(',', '.')) || 0;
    

    for (let i = 0; i < totalForm; i++){
        let quantity = parseInt($('input[name="order-' + i + '-quantity"]').val());

        let price = parseFloat($('.items-' + i + '-price').text().replace(',', '.'));
        quantityArr[i] = quantity;
        priceArr[i] = price ? price : 0;
        totalPriceArr[i] = Number((price * quantity).toFixed(2))
    }

    if (!orderTotalQuantity){
        updateTotalQuantity();
    }

    $orderForm = $('.order_form')
    $orderForm.on('change', 'input[type="number"]', function (event){
        orderItemNum = parseInt(event.target.name.replace('order-', '').replace('-quantity', ''));
        if (priceArr[orderItemNum]) {
            orderItemQuantity = parseInt(event.target.value);
            deltaQuantity = orderItemQuantity - quantityArr[orderItemNum];
            quantityArr[orderItemNum] = orderItemQuantity;
            renderTotalCostItem(orderItemNum)
            orderSummaryUpdate(priceArr[orderItemNum], deltaQuantity)
        }
    });

    $orderForm.on('change','input[type="checkbox"]', function (event){
        orderItemNum = parseInt(event.target.name.replace('order-', '').replace('-DELETE', ''));
        if (event.target.checked){
            deltaQuantity = -quantityArr[orderItemNum];
        } else {
            deltaQuantity = quantityArr[orderItemNum];
        }
        orderSummaryUpdate(priceArr[orderItemNum], deltaQuantity);
    });

    $('.order_form select').change(function (event){
        let t_href = event.target;
        $.ajax({
            url: "/orders/update/ajax/" + t_href.value + "/",
            success: function (data) {
                let num = parseInt(t_href.name.replace('order-', '').replace('-product', ''));
                let item = $('.items-' + num + '-price')

                item.html(Number(data['result']).toString().replace('.', ','));
                quantityArr[num] = parseInt($('input[name="order-' + num + '-quantity"]').val());
                priceArr[num] = parseFloat(item.text().replace(',', '.'));
                console.log(priceArr)
            }
        });

    });


    $('.formset_row').formset({
        addText: 'добавить продукт',
        deleteText: 'удалить',
        prefix: 'orderitems',
        removed: deleteOrderItem
    });


}
