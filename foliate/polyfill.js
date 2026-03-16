if (!Object.groupBy) {
    Object.groupBy = function (items, callback) {
        return items.reduce((result, item) => {
            const key = callback(item);
            (result[key] = result[key] || []).push(item);
            return result;
        }, {});
    };
}