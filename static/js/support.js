        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            });
        });

        function generateTableOfContents() {
            const headings = document.querySelectorAll('.content h2, .content h3');
            if (headings.length > 3) {
                const tocContainer = document.createElement('div');
                tocContainer.className = 'info-box';
                tocContainer.innerHTML = '<h3>Table of Contents</h3><ul id="toc-list"></ul>';
                
                const tocList = tocContainer.querySelector('#toc-list');
                
                headings.forEach((heading, index) => {
                    const id = `section-${index}`;
                    heading.id = id;
                    
                    const listItem = document.createElement('li');
                    listItem.innerHTML = `<a href="#${id}">${heading.textContent}</a>`;
                    tocList.appendChild(listItem);
                });
                
                const firstH2 = document.querySelector('.content h2');
                if (firstH2) {
                    firstH2.parentNode.insertBefore(tocContainer, firstH2);
                }
            }
        }

        document.addEventListener('DOMContentLoaded', function() {
            generateTableOfContents();
        });