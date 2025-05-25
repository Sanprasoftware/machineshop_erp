async function calculateDuration(frm, from_time = null, to_time = null) {
    if (!from_time || !to_time) {
        frappe.throw("Both from time and to time are required.");
        return;
    }

    let start_time = new Date(`1970-01-01T${from_time}`);
    let end_time = new Date(`1970-01-01T${to_time}`);

    let diff_ms = end_time.getTime() - start_time.getTime();

    if (diff_ms < 0) {
        let before_24 = (24 * 60 * 60 * 1000) - start_time.getTime() % (24 * 60 * 60 * 1000); 
        let after_24 = end_time.getTime() % (24 * 60 * 60 * 1000); 
        let total_time = before_24 + after_24;
        const hours =(total_time) / (1000 * 60 * 60);
        const minutes = (total_time) / (1000 * 60);
        frm.set_value('hours', Math.floor(hours));
        frm.set_value('minutes', Math.floor(minutes))
        return;
    }


    const hours =(diff_ms) / (1000 * 60 * 60);
    const minutes = (diff_ms) / (1000 * 60);
    frm.set_value('hours', Math.floor(hours));
    frm.set_value('minutes', Math.floor(minutes))
}

frappe.ui.form.on("MachineShop Shift", {
    from_time: async function (frm) {

        if (frm.doc.to_time && frm.doc.from_time) {
            await calculateDuration(frm, frm.doc.from_time, frm.doc.to_time);
        }
    },
    to_time: async function (frm) {
        if (frm.doc.to_time && frm.doc.from_time) {
            await calculateDuration(frm, frm.doc.from_time, frm.doc.to_time);
        }
    },
    before_save: async function (frm) {
        await calculateDuration(frm, frm.doc.from_time, frm.doc.to_time);
    }
});
