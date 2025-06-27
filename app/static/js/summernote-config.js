$(document).ready(function() {
    $('#summernote').summernote(
        {   
            tabsize: 2,
            height: 120,
            codemirror: { 
                theme: 'monokai'
            }, 
            toolbar: [
                ['style', ['bold', 'italic', 'underline']],                
                ['fontsize', ['fontsize']],
                ['color', ['color']],
                ['para', ['ul', 'ol', 'paragraph']]
]
        }
    );
});

$(document).ready(function() {
    $('#second_summernote').summernote(
        {   
            tabsize: 2,
            height: 120,
            codemirror: { 
                theme: 'monokai'
            }, 
            toolbar: [
                ['style', ['bold', 'italic', 'underline']],                
                ['fontsize', ['fontsize']],
                ['color', ['color']],
                ['para', ['ul', 'ol', 'paragraph']]
]
        }
    );
});
