package com.vm.upthrive.entity;


import jakarta.persistence.*;
import lombok.*;

import java.util.List;

@Entity
@Table(name = "companies")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Company {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String companyName;

    private String website;

    private String location;

    private String industry;

    @Column(columnDefinition="TEXT")
    private String description;

    private String logoUrl;

    @OneToMany(mappedBy = "company", cascade = CascadeType.ALL)
    private List<Opportunity> opportunities;
}
