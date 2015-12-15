Ext.define('Xmin.util.GetLines', {
    singleton: true,
    func : function(element) {
        void function $getLines($){
            function countLines($element){
                // Расчитываем количество символов в первой и второй
                // текста в html елементе и обрезаем их с добавлением троеточия.
                var lines = 0;
                var greatestOffset = void 0;
                var first = '';
                var second = '';
                $element.find('character').each(function(){
                    if(!greatestOffset || this.offsetTop > greatestOffset){
                        greatestOffset = this.offsetTop;
                        ++lines;
                    }

                    if (lines == 1) {
                        first += this.textContent;
                    }

                    if (lines == 2) {
                        second += this.textContent;
                    }

                });

                if (second.length > 14) {
                    second = second.slice(0, 14);
                    second += '...';
                    lines = 3;
                }

                if (first.length > 14) {
                    first = first.slice(0, 14);
                    first += '...';
                    lines = 3;
                }
                else {
                    first += second;
                }
                return [lines, first];
            }

            $.fn.getLines = function $getLines(){
                var lines = 0;
                var clean = this;
                var dirty = this.clone();
                (function wrapCharacters(fragment){
                    var parent = fragment;
                    $(fragment).contents().each(function(){
                        if(this.nodeType === Node.ELEMENT_NODE){
                            wrapCharacters(this);
                        }
                        // Для текстового блока оборачиваем каждый символ в тег <character></>
                        else if(this.nodeType === Node.TEXT_NODE){
                            void function replaceNode(text){
                                var characters = document.createDocumentFragment();
                                text.nodeValue.replace(/[\s\S]/gm, function wrapCharacter(character){
                                    characters.appendChild($('<character>' + character + '</>')[0]);
                                });
                                parent.replaceChild(characters, text);
                            }(this);
                        }
                    });
                }(dirty[0]));
                clean.replaceWith(dirty);
                var res = countLines(dirty);
                dirty.replaceWith(clean);
                return res;
            };
        }(jQuery);

    return $(element).getLines();
    }
});
