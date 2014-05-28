
(function($){

  $(document).ready(function(){

    var converter = new Markdown.Converter(),
        text_area = document.createElement("textarea"),
        $editors = $(".mdEditorTextArea");

    function isEventSupported( event_name ) {
      var event_name = "on" + event_name,
          is_supported = (event_name in text_area);

      if ( !is_supported ) {
        text_area.setAttribute(eventName, "return;");
        is_supported = (typeof text_area[eventName] === "function");
      }
      return is_supported;
    }

    function refreshEditor() {
      var $frame = $(this).parents(".mdEditorFrame"),
          $preview = $frame.find(".mdEditorPreview");
      this.style.height = "1px";
      this.style.height = this.scrollHeight + "px";
      $preview.html( converter.makeHtml(this.value) );
    }

    $editors.on("focus", function(){
      $(this).parents(".mdEditorFrame").addClass("mdEditorFrameFocus");
    });
    $editors.on("blur", function(){
      $(this).parents(".mdEditorFrame").removeClass("mdEditorFrameFocus");
    });
    if ( isEventSupported("input") ) {
      $editors.on("input", refreshEditor);
    } else {
      $editors.on("keyup", refreshEditor);
    }
    $editors.on("change", refreshEditor);
    $editors.change();

  });

})(window.jQuery || grp.jQuery || django.jQuery);
