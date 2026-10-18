function _makeMassPoints(
    _AMap,
    _map,
    _massPoints,
    _layer,
    _clickcb) {
    if (_layer) {
        _layer.show()
    } else {
        // 创建 AMap.LabelsLayer 图层
        let temp_layer = new _AMap.LabelsLayer({
            zooms: [3, 20],
            zIndex: 1000,
            collision: false
        })
        // 将图层添加到地图
        _map.add(temp_layer)

        let markers = []
        let icon = {
            type: 'image',
            image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png',
            size: [12, 18],
            anchor: 'bottom-center',
        };

        for (let i = 0; i < _massPoints.length; i++) {
            let currentPosition = _massPoints[i]
            let curData = {
                name: i + 1,
                position: currentPosition,
                extData: i + 1,
                icon
            }

            let labelMarker = new _AMap.LabelMarker(curData);
            markers.push(labelMarker)

            labelMarker.on("click", e => {
                _clickcb(e.target._originOpts.extData)
                // vueObj._buttonClick(e.target._originOpts.extData);
            })
        }

        temp_layer.add(markers);

        // vueObj.setLayer(temp_layer);
        return temp_layer;
    }
}

function _cleanMassPoints(layer) {
    if (layer) {
        layer.hide()
    }
}

export { _makeMassPoints, _cleanMassPoints }