$('input[type=radio][name=vista]').change(function(){
    viewType = this.value;

    if(viewType == "0"){
        createPanels(globalTotalProducts, globalFrames, globalPaths);
    }
    else {
        createPanelsCarousel(globalTotalProducts, globalFrames, globalPaths);
    }
});