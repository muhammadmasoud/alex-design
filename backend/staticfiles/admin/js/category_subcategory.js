// Dynamic subcategory selection for Django admin
(function($) {
    'use strict';

    // Define category-subcategory mappings
    const PROJECT_CATEGORIES = {
        'Residential': [
            ['Single Family Home', 'Single Family Home'],
            ['Multi Family Home', 'Multi Family Home'],
            ['Apartment Complex', 'Apartment Complex'],
            ['Townhouse', 'Townhouse'],
            ['Villa', 'Villa'],
            ['Penthouse', 'Penthouse'],
            ['Studio Apartment', 'Studio Apartment']
        ],
        'Commercial': [
            ['Office Building', 'Office Building'],
            ['Shopping Mall', 'Shopping Mall'],
            ['Restaurant', 'Restaurant'],
            ['Hotel', 'Hotel'],
            ['Retail Store', 'Retail Store'],
            ['Warehouse', 'Warehouse'],
            ['Showroom', 'Showroom'],
            ['Clinic', 'Clinic'],
            ['Bank', 'Bank']
        ],
        'Public': [
            ['School', 'School'],
            ['University', 'University'],
            ['Hospital', 'Hospital'],
            ['Museum', 'Museum'],
            ['Library', 'Library'],
            ['Government Building', 'Government Building'],
            ['Community Center', 'Community Center'],
            ['Religious Building', 'Religious Building'],
            ['Transportation Hub', 'Transportation Hub']
        ],
        'Industrial': [
            ['Manufacturing Plant', 'Manufacturing Plant'],
            ['Power Plant', 'Power Plant'],
            ['Chemical Plant', 'Chemical Plant'],
            ['Food Processing', 'Food Processing'],
            ['Automotive Plant', 'Automotive Plant'],
            ['Steel Mill', 'Steel Mill'],
            ['Oil Refinery', 'Oil Refinery'],
            ['Research Facility', 'Research Facility']
        ],
        'Landscape': [
            ['Public Garden', 'Public Garden'],
            ['Private Garden', 'Private Garden'],
            ['Urban Plaza', 'Urban Plaza'],
            ['Playground', 'Playground'],
            ['Sports Complex', 'Sports Complex'],
            ['Park', 'Park'],
            ['Golf Course', 'Golf Course'],
            ['Cemetery', 'Cemetery']
        ],
        'Interior': [
            ['Living Room', 'Living Room'],
            ['Kitchen', 'Kitchen'],
            ['Bedroom', 'Bedroom'],
            ['Bathroom', 'Bathroom'],
            ['Office Space', 'Office Space'],
            ['Restaurant Interior', 'Restaurant Interior'],
            ['Hotel Room', 'Hotel Room'],
            ['Reception Area', 'Reception Area']
        ],
        'Urban': [
            ['Master Planning', 'Master Planning'],
            ['Mixed Use Development', 'Mixed Use Development'],
            ['Transit Oriented', 'Transit Oriented'],
            ['Waterfront Development', 'Waterfront Development'],
            ['Historic District', 'Historic District'],
            ['Smart City', 'Smart City'],
            ['Sustainable Community', 'Sustainable Community'],
            ['Urban Renewal', 'Urban Renewal']
        ],
        'Other': [
            ['Custom Design', 'Custom Design'],
            ['Prototype', 'Prototype'],
            ['Renovation', 'Renovation'],
            ['Restoration', 'Restoration'],
            ['Conceptual', 'Conceptual'],
            ['Competition Entry', 'Competition Entry']
        ]
    };

    const SERVICE_CATEGORIES = {
        'Design': [
            ['Architectural Design', 'Architectural Design'],
            ['Interior Design', 'Interior Design'],
            ['Landscape Design', 'Landscape Design'],
            ['Urban Planning', 'Urban Planning'],
            ['Structural Design', 'Structural Design'],
            ['MEP Design', 'MEP Design'],
            ['Facade Design', 'Facade Design']
        ],
        'Planning': [
            ['Site Planning', 'Site Planning'],
            ['Master Planning', 'Master Planning'],
            ['Zoning Analysis', 'Zoning Analysis'],
            ['Feasibility Study', 'Feasibility Study'],
            ['Environmental Planning', 'Environmental Planning'],
            ['Traffic Planning', 'Traffic Planning'],
            ['Infrastructure Planning', 'Infrastructure Planning']
        ],
        'Consulting': [
            ['Design Consultation', 'Design Consultation'],
            ['Project Management', 'Project Management'],
            ['Construction Administration', 'Construction Administration'],
            ['Code Compliance', 'Code Compliance'],
            ['Sustainability Consulting', 'Sustainability Consulting'],
            ['Cost Estimation', 'Cost Estimation'],
            ['Risk Assessment', 'Risk Assessment']
        ],
        'Visualization': [
            ['3D Rendering', '3D Rendering'],
            ['Animation', 'Animation'],
            ['Virtual Reality', 'Virtual Reality'],
            ['Architectural Photography', 'Architectural Photography'],
            ['Presentation Design', 'Presentation Design'],
            ['Technical Drawing', 'Technical Drawing'],
            ['Model Making', 'Model Making']
        ]
    };

    function updateSubcategories(categorySelect, subcategorySelect, categories) {
        const selectedCategory = categorySelect.val();
        
        // Clear current subcategory options
        subcategorySelect.empty();
        subcategorySelect.append('<option value="">---------</option>');
        
        if (selectedCategory && categories[selectedCategory]) {
            // Add subcategories for selected category
            categories[selectedCategory].forEach(function(subcategory) {
                subcategorySelect.append(
                    '<option value="' + subcategory[0] + '">' + subcategory[1] + '</option>'
                );
            });
        }
    }

    function initializeCategorySubcategory() {
        const categoryField = $('#id_category');
        const subcategoryField = $('#id_subcategory');
        
        if (categoryField.length && subcategoryField.length) {
            // Determine which categories to use based on the current model
            let categories;
            if (window.location.href.includes('/project/')) {
                categories = PROJECT_CATEGORIES;
            } else if (window.location.href.includes('/service/')) {
                categories = SERVICE_CATEGORIES;
            } else {
                return; // Not a project or service form
            }

            // Store current subcategory value
            const currentSubcategory = subcategoryField.val();

            // Update subcategories when category changes
            categoryField.on('change', function() {
                updateSubcategories(categoryField, subcategoryField, categories);
            });

            // Initialize subcategories on page load
            updateSubcategories(categoryField, subcategoryField, categories);
            
            // Restore the previously selected subcategory if it exists
            if (currentSubcategory) {
                subcategoryField.val(currentSubcategory);
            }
        }
    }

    // Initialize when DOM is ready
    $(document).ready(function() {
        initializeCategorySubcategory();
    });

})(django.jQuery);
