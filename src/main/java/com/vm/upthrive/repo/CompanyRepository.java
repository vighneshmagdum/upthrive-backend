package com.vm.upthrive.repo;

import com.vm.upthrive.entity.Company;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface CompanyRepository extends JpaRepository<Company,Long> {

    Optional<Company> findByCompanyName(String companyName);
    boolean existsByCompanyName(String companyName);

}
