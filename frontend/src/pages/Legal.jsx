import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Legal.css';

const ADMIN_USERNAMES = ['yems', "01yem's"];

function Legal() {
    const navigate = useNavigate();
    const { user } = useAuth();
    const isAdmin = ADMIN_USERNAMES.includes(user?.username);

    const authorName = isAdmin ? 'Yems junior lendola' : 'L\'équipe YELMON';
    const authorEmail = isAdmin ? 'yemsjuniorlendola@gmail.com' : 'support@yelmon.dev';
    const authorLocation = isAdmin ? 'Kinshasa, RDC' : '***';

    return (
        <div className="legal-page">
            <div className="legal-container">
                <button onClick={() => navigate('/')} className="legal-back">
                    ← Retour au tableau de bord
                </button>

                <div className="legal-header">
                    <div className="legal-logo">⚖</div>
                    <h1>Politique & Conditions d'Utilisation</h1>
                    <p className="legal-subtitle">YELMON Dev X — Document juridique officiel</p>
                    <p className="legal-date">Dernière mise à jour : 16 août 2026 · Version 1.0.0</p>
                </div>

                <div className="legal-content">

                    <div className="legal-warning">
                        <div className="warning-icon">⛔</div>
                        <div className="warning-text">
                            <strong>AVERTISSEMENT JURIDIQUE IMPORTANT</strong>
                            <p>
                                Ce logiciel et l'ensemble de ses composants (code binaire, scripts,
                                algorithmes, modèles, interfaces, designs, documentation) sont la
                                propriété exclusive de <strong>{authorName}</strong>. Toute
                                reproduction, copie, distribution, ingénierie inverse ou utilisation
                                non autorisée est strictement interdite et constitue une atteinte
                                aux droits de propriété intellectuelle passible de poursuites
                                judiciaires.
                            </p>
                        </div>
                    </div>

                    <section className="legal-section">
                        <h2>1. Objet du document</h2>
                        <p>
                            Le présent document établit les conditions régissant l'utilisation du
                            logiciel <strong>YELMON Dev X</strong> (ci-après « le Logiciel »),
                            édité et développé exclusivement par <strong>{authorName}</strong>
                            (ci-après « l'Auteur »). En installant, accédant ou utilisant le
                            Logiciel, l'utilisateur (ci-après « l'Utilisateur ») reconnaît avoir
                            pris connaissance des présentes conditions et s'engage à les respecter
                            sans réserve.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>2. Propriété intellectuelle</h2>
                        <p>
                            L'ensemble des éléments constitutifs de YELMON Dev X sont protégés par
                            les lois relatives à la propriété intellectuelle, aux droits d'auteur
                            et aux brevets. Ces éléments incluent, sans s'y limiter :
                        </p>
                        <ul className="legal-list">
                            <li><strong>Code binaire et exécutables compilés</strong> — Toute forme de représentation machine</li>
                            <li><strong>Code source et scripts</strong> — Dans tous les langages de programmation</li>
                            <li><strong>Modèles d'intelligence artificielle</strong> — Algorithmes, réseaux neuronaux, poids de modèles, moteurs RAG</li>
                            <li><strong>Interfaces utilisateur</strong> — Designs, animations, composants visuels, thèmes</li>
                            <li><strong>Propriétés de marque</strong> — Noms, logos, marques commerciales et branding</li>
                            <li><strong>Documentation</strong> — Manuels, guides et supports écrits</li>
                            <li><strong>Protocoles et API</strong> — Structures de données et interfaces</li>
                        </ul>
                    </section>

                    <section className="legal-section">
                        <h2>3. Licence d'utilisation</h2>
                        <p>
                            L'Auteur accorde à l'Utilisateur une licence <strong>limitée,
                            non exclusive, non transférable et révocable</strong> d'installation
                            et d'utilisation du Logiciel sur un seul appareil personnel, exclusivement
                            à des fins privées et non commerciales.
                        </p>
                        <p>
                            Cette licence n'entraîne aucun transfert de propriété ni de droit de
                            propriété intellectuelle au profit de l'Utilisateur.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>4. Interdictions formelles</h2>
                        <p>L'Utilisateur s'interdit expressément de :</p>
                        <ol className="legal-ordered">
                            <li><strong>Copier, reproduire, dupliquer</strong> tout ou partie du code binaire, du code source, des scripts ou des modèles sur quel support que ce soit ;</li>
                            <li><strong>Effectuer une ingénierie inverse</strong>, décompiler, désassembler ou tenter de dériver le code source à partir de la forme binaire ;</li>
                            <li><strong>Distribuer, sous-licencier, vendre, louer, partager</strong> le Logiciel ou toute œuvre dérivée à des tiers ;</li>
                            <li><strong>Modifier, adapter, traduire, créer des œuvres dérivées</strong> basées sur le Logiciel ;</li>
                            <li><strong>Supprimer, altérer ou masquer</strong> toute mention de droit d'auteur ou de propriété intellectuelle ;</li>
                            <li><strong>Exploiter le Logiciel</strong> pour développer, entraîner ou améliorer tout produit concurrent ;</li>
                            <li><strong>Circumventer les protections</strong> contre la copie ou les systèmes de vérification de licence ;</li>
                            <li><strong>Réclamer la paternité</strong> ou les droits d'auteur sur le Logiciel.</li>
                        </ol>
                    </section>

                    <section className="legal-section">
                        <h2>5. Protection contre la copie</h2>
                        <p>
                            YELMON Dev X intègre des mécanismes propriétaires de protection contre
                            la copie et la distribution non autorisée. Toute tentative de contourner,
                            désactiver ou supprimer ces protections est strictement interdite et
                            constitue une violation substantielle de la présente licence.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>6. Données et confidentialité</h2>
                        <p>
                            YELMON Dev X peut collecter des données d'utilisation anonymisées pour
                            améliorer la qualité du Logiciel. Aucune information personnelle
                            identifiable n'est collectée sans consentement explicite.
                        </p>
                        <p>
                            Les données générées par l'Utilisateur (code produit, historique,
                            snippets) restent la propriété de l'Utilisateur et sont stockées
                            localement sur son appareil.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>7. Garantie et responsabilité</h2>
                        <p>
                            LE LOGICIEL EST FOURNI « EN L'ÉTAT », SANS GARANTIE D'AUCUNE SORTE,
                            EXPRESSE OU IMPLICITE, Y COMPRIS LES GARANTIES DE QUALITÉ MARCHANDE,
                            D'ADÉQUATION À UN USAGE PARTICULIER ET DE NON-VIOLATION.
                        </p>
                        <p>
                            En aucun cas l'Auteur ne saurait être tenu responsable des dommages
                            indirects, accessoires, spéciaux, consécutifs ou punitifs résultant
                            de l'utilisation du Logiciel.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>8. Mises à jour et évolutions</h2>
                        <p>
                            L'Auteur se réserve le droit de modifier, améliorer ou mettre à jour
                            le Logiciel à tout moment, sans obligation de préavis. Les mises à jour
                            peuvent être facultatives ou obligatoires pour maintenir la compatibilité
                            et la sécurité du Logiciel.
                        </p>
                        <p>
                            L'Utilisateur accepte que des modifications puissent être apportées au
                            Logiciel sans consentement préalable, y compris des changements de
                            fonctionnalités, d'interfaces ou de conditions d'utilisation.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>9. Compatibilité système</h2>
                        <p>
                            Le Logiciel est conçu pour fonctionner sur les systèmes d'exploitation
                            et configurations matérielles spécifiés dans la documentation technique.
                            L'Auteur ne garantit pas la compatibilité avec toutes les
                            configurations existantes ou futures.
                        </p>
                        <p>
                            L'Utilisateur est responsable de vérifier la compatibilité de son
                            système avant l'installation du Logiciel.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>10. Support technique</h2>
                        <p>
                            L'Auteur peut, à sa seule discrétion, fournir un support technique
                            pour l'utilisation du Logiciel. Ce support n'est en aucun cas obligatoire
                            et peut être modifié, suspendu ou supprimé sans préavis.
                        </p>
                        <p>
                            Les demandes de support doivent être adressées exclusivement via les
                            canaux officiels indiqués à l'article 30 du présent document.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>11. Utilisation par les mineurs</h2>
                        <p>
                            Le Logiciel est destiné aux personnes âgées de 16 ans ou plus. Les
                            mineurs de moins de 16 ans ne sont pas autorisés à utiliser le Logiciel
                            sans le consentement explicite d'un parent ou tuteur légal.
                        </p>
                        <p>
                            L'Auteur décline toute responsabilité en cas d'utilisation non
                            autorisée par des mineurs.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>12. Utilisation commerciale</h2>
                        <p>
                            Toute utilisation commerciale du Logiciel est strictement interdite
                            sans l'obtention préalable d'une licence commerciale distincte
                            accordée par l'Auteur. Cela inclut, sans s'y limiter :
                        </p>
                        <ul className="legal-list">
                            <li>L'intégration du Logiciel dans un produit ou service commercial</li>
                            <li>L'utilisation du Logiciel dans le cadre d'activités génératrices de revenus</li>
                            <li>La fourniture du Logiciel comme service à des tiers</li>
                            <li>L'utilisation des modèles d'IA pour des fins commerciales</li>
                        </ul>
                    </section>

                    <section className="legal-section">
                        <h2>13. Export et réglementation</h2>
                        <p>
                            L'Utilisateur est seul responsable du respect des lois et réglementations
                            applicables en matière d'export de logiciels dans sa juridiction. Le
                            Logiciel ne doit pas être exporté, réexporté ou transféré vers des pays,
                            entités ou personnes faisant l'objet de restrictions internationales.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>14. Sécurité informatique</h2>
                        <p>
                            L'Utilisateur s'engage à utiliser le Logiciel de manière sécurisée et
                            à ne pas tenter de compromettre la sécurité du Logiciel, de ses serveurs
                            ou de ses infrastructures associées. Cela inclut l'interdiction de :
                        </p>
                        <ul className="legal-list">
                            <li>Introduire des logiciels malveillants, virus ou codes nocifs</li>
                            <li>Tenter des attaques par déni de service ou d'ingénierie sociale</li>
                            <li>Accéder non autorisé aux systèmes ou données de l'Auteur</li>
                            <li>Intercepter ou altérer les communications réseau du Logiciel</li>
                        </ul>
                    </section>

                    <section className="legal-section">
                        <h2>15. Propriété des données générées</h2>
                        <p>
                            Le code, les snippets et les contenus générés par l'intermédiaire du
                            Logiciel restent la propriété intellectuelle de l'Utilisateur, sous
                            réserve que ceux-ci ne constituent pas des copies ou des dérivés du
                            Logiciel lui-même.
                        </p>
                        <p>
                            L'Auteur ne revendique aucun droit de propriété sur les créations
                            de l'Utilisateur, mais se réserve le droit d'utiliser les données
                            anonymisées pour améliorer les performances du Logiciel.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>16. Limite de performance</h2>
                        <p>
                            Les performances du Logiciel (temps de génération, précision des
                            résultats, disponibilité) peuvent varier en fonction de la charge
                            serveur, de la complexité des demandes et des ressources disponibles.
                            L'Auteur ne garantit aucun niveau de performance spécifique.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>17. Contenu généré par intelligence artificielle</h2>
                        <p>
                            Le Logiciel utilise des modèles d'intelligence artificielle pour
                            générer du code et du contenu. L'Auteur ne garantit pas l'exactitude,
                            la complétude ou la fiabilité du contenu généré. L'Utilisateur est
                            seul responsable de la vérification et de la validation de tout
                            contenu produit par le Logiciel avant utilisation.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>18. Utilisation des données d'entraînement</h2>
                        <p>
                            Les modèles d'IA du Logiciel peuvent avoir été entraînés sur des
                            données publiques et propriétaires. Aucune donnée d'entraînement
                            n'est accessible, extractible ou reproductible par l'Utilisateur.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>19. Liens et services tiers</h2>
                        <p>
                            Le Logiciel peut contenir des liens vers des services tiers ou
                            interagir avec des API externes. L'Auteur n'exerce aucun contrôle
                            sur ces services et décline toute responsabilité concernant leur
                            contenu, leurs politiques de confidentialité ou leurs pratiques.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>20. Force majeure</h2>
                        <p>
                            L'Auteur ne saurait être tenu responsable de l'inexécution de ses
                            obligations en cas de force majeure, incluant mais sans s'y limiter :
                            catastrophes naturelles, conflits armés, interruptions d'alimentation
                            électrique, pannes réseau, cyberattaques ou toute autre circonstance
                            échappant au contrôle raisonnable de l'Auteur.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>21. Séparabilité des clauses</h2>
                        <p>
                            Si l'une quelconque des dispositions du présent document est déclarée
                            invalide ou inapplicable par une juridiction compétente, les autres
                            dispositions restent pleinement en vigueur et continuent de produire
                            leurs effets juridiques.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>22. Révision du contrat</h2>
                        <p>
                            L'Auteur se réserve le droit de modifier les présentes conditions
                            à tout moment. Les modifications prennent effet dès leur publication
                            dans le Logiciel ou sur le site officiel. L'utilisation continue
                            du Logiciel après publication des modifications constitue une
                            acceptation tacite des nouvelles conditions.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>23. Cession de licence</h2>
                        <p>
                            L'Utilisateur ne peut ni céder, ni transférer, ni sous-licencier
                            tout ou partie des droits accordés par la présente licence à des
                            tiers, sans l'écrit préalable et expresse de l'Auteur.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>24. Indemnisation</h2>
                        <p>
                            L'Utilisateur s'engage à indemniser, défendre et dégager de
                            responsabilité l'Auteur contre toute réclamation, action judiciaire,
                            dommage, perte ou dépense découlant de l'utilisation non autorisée
                            du Logiciel ou de la violation des présentes conditions.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>25. Limitation temporelle</h2>
                        <p>
                            Les mécanismes de protection contre la copie et les systèmes de
                            vérification de licence sont conçus pour fonctionner de manière
                            permanente. Toute tentative de désactivation, même après une
                            période prolongée d'utilisation, constitue une violation des
                            présentes conditions.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>26. Acceptation tacite</h2>
                        <p>
                            L'installation, l'exécution ou l'utilisation quelconque du Logiciel
                            après réception des présentes conditions constitue une acceptation
                            entière et sans réserve de l'ensemble de leurs dispositions.
                            L'Utilisateur renonce expressément à invoquer tout moyen de droit
                            tiré de l'ignorance de ces conditions.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>27. Conservation des preuves</h2>
                        <p>
                            L'Auteur se réserve le droit de conserver des enregistrements
                            techniques, des journaux d'activité et des traces de connexion
                            comme preuve de l'utilisation du Logiciel, dans le respect des
                            lois applicables en matière de protection des données.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>28. Clause pénale</h2>
                        <p>
                            En cas de violation avérée des présentes conditions, l'Utilisateur
                            s'expose à des dommages-intérêts d'un montant minimum de
                            <strong> 10 000 USD (dix mille dollars américains)</strong>, sans
                            préjudice du droit de l'Auteur de solliciter des dommages-intérêts
                            complémentaires à hauteur du préjudice réel subi.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>29. Médiation préalable</h2>
                        <p>
                            Avant toute action judiciaire, les parties s'engagent à tenter de
                            résoudre leurs différends par la médiation, pendant une durée minimum
                            de trente (30) jours. La médiation sera conduite à {authorLocation},
                            par un médiateur agréé désigné d'un commun accord.
                        </p>
                    </section>

                    <section className="legal-section">
                        <h2>30. Contact officiel</h2>
                        <p>
                            Pour toute question relative à la présente licence, demandes
                            d'autorisation ou signalement de violations, veuillez contacter :
                        </p>
                        <div className="legal-contact">
                            <p><strong>Auteur & Éditeur :</strong> {authorName}</p>
                            <p><strong>Logiciel :</strong> YELMON Dev X</p>
                            <p><strong>Email :</strong> {authorEmail}</p>
                            <p><strong>Version :</strong> 1.0.0</p>
                            <p><strong>Juridiction :</strong> {authorLocation}</p>
                        </div>
                    </section>

                    <div className="legal-signature">
                        <p>
                            En utilisant YELMON Dev X, vous reconnaissez avoir lu, compris et
                            accepté l'ensemble des termes et conditions de la présente licence
                            composée de trente (30) articles.
                        </p>
                        <div className="legal-seal">
                            <div className="seal-mark">Y</div>
                            <div className="seal-text">
                                <strong>© 2026 {authorName}</strong>
                                <span>Tous droits réservés</span>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    );
}

export default Legal;
