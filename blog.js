/* Comportements partages par les pages d'article.
   Aucun contenu n'est cree ici : le HTML est complet sans JavaScript.
   1. le sommaire est replie par defaut sous 1024 px ;
   2. scrollspy : la section visible est mise en evidence dans le sommaire. */
(function () {
  'use strict';

  var sommaire = document.querySelector('.col-toc .toc');
  var liens = [].slice.call(document.querySelectorAll('.col-toc .toc a[href^="#"]'));
  if (!sommaire || !liens.length) return;

  // 1. repli du sommaire sur petit ecran
  var petitEcran = window.matchMedia('(max-width: 1023px)');
  function ajusterRepli(mq) { if (mq.matches) sommaire.removeAttribute('open'); else sommaire.setAttribute('open', ''); }
  ajusterRepli(petitEcran);
  if (petitEcran.addEventListener) petitEcran.addEventListener('change', ajusterRepli);
  // seconde passe apres le chargement complet, la largeur est alors definitive
  window.addEventListener('load', function () { ajusterRepli(petitEcran); });

  // 2. scrollspy
  if (!('IntersectionObserver' in window)) return;

  var parId = {};
  var cibles = [];
  liens.forEach(function (a) {
    var cible = document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1)));
    if (cible) { parId[cible.id] = a; cibles.push(cible); }
  });
  if (!cibles.length) return;

  var visibles = [];
  function activer(id) {
    liens.forEach(function (a) { a.classList.remove('actif'); });
    if (parId[id]) parId[id].classList.add('actif');
  }

  var observateur = new IntersectionObserver(function (entrees) {
    entrees.forEach(function (e) {
      var i = visibles.indexOf(e.target);
      if (e.isIntersecting && i === -1) visibles.push(e.target);
      else if (!e.isIntersecting && i !== -1) visibles.splice(i, 1);
    });
    if (!visibles.length) return;
    // la premiere section visible dans l'ordre du document fait foi
    var premiere = visibles.slice().sort(function (a, b) {
      return cibles.indexOf(a) - cibles.indexOf(b);
    })[0];
    activer(premiere.id);
  }, { rootMargin: '-96px 0px -70% 0px', threshold: 0 });

  cibles.forEach(function (c) { observateur.observe(c); });
})();
