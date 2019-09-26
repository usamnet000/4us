

$(function(){
  /*
   * For the sake keeping the code clean and the examples simple this file
   * contains only the plugin configuration & callbacks.
   * 
   * UI functions ui_* can be located in: demo-ui.js
   */
  $('#drag-and-drop-zone').dmUploader({ //
    url: "",
    maxFileSize: 3000000, // 3 Megs 
    onDragEnter: function(){
      // Happens when dragging something over the DnD area
      this.addClass('active');
    },
    onDragLeave: function(){
      // Happens when dragging something OUT of the DnD area
      this.removeClass('active');
    },
    onInit: function(){
      // Plugin is ready to use
      ui_add_log('تهيئة :)', 'info');
    },
    onComplete: function(){
      // All files in the queue are processed (success or error)
      ui_add_log('الانتهاء من جميع التحميل المعلق');
    },
    onNewFile: function(id, file){
      // When a new file is added using the file selector or the DnD area

      ui_add_log('تمت إضافة ملف جديد #' + id);
      ui_multi_add_file(id, file);
    },
    onBeforeUpload: function(id){
      // about tho start uploading a file
      ui_add_log('بدء تحميل من #' + id);
      ui_multi_update_file_status(id, 'uploading', 'تحميل...');
      ui_multi_update_file_progress(id, 0, '', true);
    },
    onUploadCanceled: function(id) {
      // Happens when a file is directly canceled by the user.
      ui_multi_update_file_status(id, 'warning', 'تم الانهاء قبل التحميل');
      ui_multi_update_file_progress(id, 0, 'warning', false);
    },
    onUploadProgress: function(id, percent){
      // Updating file progress
      ui_multi_update_file_progress(id, percent);
    },
    onUploadSuccess: function(id, data){
      // A file was successfully uploaded
      ui_add_log('Server Response for file #' + id + ': ' + JSON.stringify(data));
      ui_add_log('تحميل الملف #' + id + ' COMPLETED', 'success');
      ui_multi_update_file_status(id, 'success', 'اكتمال التحميل');
      ui_multi_update_file_progress(id, 100, 'success', false);
    },
    onUploadError: function(id, xhr, status, message){
      ui_multi_update_file_status(id, 'خطر', message);
      ui_multi_update_file_progress(id, 0, 'خطر', false);
    },
    onFallbackMode: function(){
      // When the browser doesn't support this plugin :(
      ui_add_log('البرنامج غير قادر على هذا المتصفح ، تشغيل الاتصال بالرجوع', 'danger');
    },
    onFileSizeError: function(file){
      ui_add_log('حجم الملف \'' + file.name + '\' تجاوز الحد الزائد', 'danger');
    }
  });
});