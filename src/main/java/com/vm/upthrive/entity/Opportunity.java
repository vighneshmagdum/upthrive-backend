package com.vm.upthrive.entity;

import com.vm.upthrive.enums.OpportunityType;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import com.vm.upthrive.enums.OpportunityStatus;

@Entity
@Table(name ="opportunities")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Opportunity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String title;

    @Column(columnDefinition="TEXT")
    private String description;

    @ManyToOne
    @JoinColumn(name ="companyid",nullable =false)
    private Company company;

    private String location;

    @Enumerated(EnumType.STRING)
    private OpportunityType type;

    private String category;

    private String skillsRequired;

    private String applicationLink;

    private LocalDate deadline;

    @Enumerated(EnumType.STRING)
    private OpportunityStatus status;

    private LocalDateTime createdAt;
}
